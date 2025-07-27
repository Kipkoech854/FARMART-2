from flask import Blueprint, request, jsonify, Response
from App.services.Order_services import OrderService
from App.Schema.Order_schema import OrderSchema
from datetime import datetime, timezone
from decimal import Decimal
from App.models.Orders import Order, OrderItem
import requests
from App.extensions import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from App.Utils.Order_email_senders import send_order_confirmation_to_user, send_order_confirmation_to_farmers
from functools import wraps
from App.Utils.mail_utils import group_items_by_farmer_util_for_user, group_items_by_farmer_util_for_farmer, get_farmer_contact, get_user_contact


Order_bp = Blueprint('Order_bp', __name__)


def get_jwt_role():
    jwt_data = get_jwt()
    return jwt_data.get("role") 


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            role = claims.get("role")
            if role not in roles:
                return jsonify({"error": "Forbidden"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


@Order_bp.route('/create', methods=['POST'])
@jwt_required()
def create_order():
    print("🟢 Request received to create order")
    data = request.get_json()

    required_fields = ['amount', 'pickup_station', 'total', 'payment_method', 'delivery_method', 'items']
    missing_fields = [field for field in required_fields if not data.get(field)]

    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    user_id = get_jwt_identity()
    amount = data['amount']
    pickup_station = data['pickup_station']
    total = data['total']
    payment_method = data['payment_method']
    delivery_method = data['delivery_method']
    items = data['items']

    # Create Order
    order = OrderService.create_order(user_id, amount, delivery_method, pickup_station, payment_method, total)

    # Create Order Items
    for item in items:
        animal_id = item.get('animal_id')
        quantity = item.get('quantity')
        price_at_order_time = item.get('price_at_order_time')

        # Optional: validate each item
        if not all([animal_id, quantity, price_at_order_time]):
            return jsonify({"error": "Each item must include 'animal_id', 'quantity', and 'price_at_order_time'"}), 400
        
        animal = Animal.query.get(animal_id)
        if not animal:
            return jsonify({"error": f"Animal with id {animal_id} not found"}), 404

        farmer_id = animal.farmer_id

        print(f"Creating OrderItem: animal_id={animal_id}, quantity={quantity}, farmer_id={farmer_id}")

        OrderService.create_order_Item(order.id, animal_id, quantity, price_at_order_time, farmer_id)
       

    order_schema = OrderSchema()
    full_order = order_schema.dump(order)

    created_at = datetime.now(timezone.utc)

    send_order_confirmation_to_user(user_id, order.id, created_at, amount, full_order.get('items', []))
    send_order_confirmation_to_farmers(full_order.get('items', []))

    return jsonify({"message": "Order created successfully!"}), 201





@Order_bp.route('/all', methods=['GET'])
@jwt_required()
@role_required("farmer", "customer")
def past_orders():
    verify_jwt_in_request()
    
    user_id = get_jwt_identity()
    role = get_jwt_role()

    # 1. Get orders based on role
    if role == "customer":
        orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    else:
        orders = Order.query.filter(Order.items.any(OrderItem.farmer_id == user_id)).all()

    if not orders:
        return jsonify([{'error': 'empty order history'}]), 404

    full_orders = []

    for order in orders:
        # 2. Extract order items
        items = [
            {
                "animal_id": item.animal_id,
                "quantity": item.quantity,
                "price_at_order_time": float(item.price_at_order_time)
            } for item in order.items
        ]

        # 3. Enrich animal data based on role
        if role == "customer":
            enriched_animals = group_items_by_farmer_util_for_user(items)
        elif role == "farmer":
            enriched_animals = group_items_by_farmer_util_for_farmer(user_id=user_id, items=items)
        else:
            enriched_animals = []

        # 4. Build base order response
        order_dict = {
            "id": order.id,
            "status": order.status,
            "paid": order.paid,
            "delivered": order.delivered,
            "amount": float(order.amount),
            "pickup_station": order.pickup_station,
            "total": order.total,
            "payment_method": order.payment_method,
            "created_at": order.created_at.isoformat(),
            "animals": enriched_animals
        }

        # 5. If farmer, attach customer contact info
        if role == "farmer":
            user_info = get_user_contact(order.user_id)
            if user_info:
                order_dict["user_info"] = {
                    "email": user_info.get("email"),
                    "username": user_info.get("username"),
                    "profile_picture": user_info.get("profile_picture")
                }

        full_orders.append(order_dict)

    return jsonify(full_orders), 200



@Order_bp.route('/<string:order_id>', methods=['GET'])
@jwt_required()
@role_required("farmer", "customer")
def get_order_by_id(order_id):
    verify_jwt_in_request()
    user_id = get_jwt_identity()
    role = get_jwt_role()

    order = Order.query.filter_by(id=order_id).first()

    if not order:
        return jsonify({'error': 'Order not found'}), 404

    if role == 'customer' and order.user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403

    order_items = OrderItem.query.filter_by(order_id=order.id).all()
    item_dicts = [
        {
            "animal_id": item.animal_id,
            "quantity": item.quantity,
            "price_at_order_time": str(item.price_at_order_time)
        }
        for item in order_items
    ]

    # Enrich animals
    if role == 'customer':
        enriched_animals = group_items_by_farmer_util_for_user(item_dicts)
    else:
        enriched_animals = group_items_by_farmer_util_for_farmer(user_id, item_dicts)
        if not enriched_animals:
            return jsonify({'error': 'Access denied'}), 403

    order_data = OrderSchema().dump(order)
    order_data['animals'] = enriched_animals

    # Add contact info
    if role == 'farmer':
        user_info = get_user_contact(order.user_id)
        if user_info:
            order_data['user_info'] = {
                'email': user_info.get('email'),
                'username': user_info.get('username'),
                'profile_picture': user_info.get('profile_picture')
            }

    elif role == 'customer':
        # Get unique farmer IDs from enriched_animals
        farmer_infos = []
        for group in enriched_animals:
            farmer_id = group.get("farmer_id")
            if farmer_id:
                contact = get_farmer_contact(farmer_id)
                if contact:
                    farmer_infos.append({
                        "farmer_id": farmer_id,
                        "username": contact.get("username"),
                        "email": contact.get("email"),
                        "profile_picture": contact.get("profile_picture")
                    })

        order_data['farmer_info'] = farmer_infos

    return jsonify(order_data), 200



@Order_bp.route('/status', methods=['GET'])
@jwt_required()
def get_orders_by_status():
    verify_jwt_in_request()
    user_id = get_jwt_identity()
    role = get_jwt()['role']
    status_param = request.args.get('status', '').lower()

    valid_statuses = ['pending', 'confirmed', 'rejected']
    if status_param not in valid_statuses:
        return jsonify({'error': f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}), 400

    query = Order.query.filter(Order.status.ilike(f'%{status_param}%')).order_by(Order.created_at.desc())

    if role == 'user':
        query = query.filter(Order.user_id == user_id)
    elif role == 'farmer':
        query = query.filter(
            Order.items.any(
                OrderItem.animal.has(Animal.farmer_id == user_id)
            )
        )

    results = query.all()
    if not results:
        return jsonify([{'error': f'No {status_param} orders available'}]), 404

    enriched_orders = []

    for order in results:
        enriched_items = []

        # Get user info (always safe, used only if role == farmer)
        user_info = get_user_contact(order.user_id) if order.user_id else {}

        for item in order.items:
            animal = Animal.query.get(item.animal_id)
            if not animal:
                continue

            # Farmer info for this animal
            farmer_info = get_farmer_contact(animal.farmer_id) if animal.farmer_id else {}

            enriched_item = {
                "animal_id": animal.id,
                "name": animal.name,
                "type": animal.type,
                "breed": animal.breed,
                "age": animal.age,
                "price": float(animal.price),
                "description": animal.description,
                "is_available": animal.is_available,
                "images":animal.images,
                "image_count": len(animal.images),
                "quantity": item.quantity,
                "price_at_order_time": float(item.price_at_order_time),
            }

            
            if role == "user":
                enriched_item.update({
                    "farmer_email": farmer_info.get("email"),
                    "farmer_username": farmer_info.get("username"),
                    "farmer_picture": farmer_info.get("profile_picture")
                })

            enriched_items.append(enriched_item)

        order_info = {
            "id": order.id,
            "user_id": order.user_id,
            "status": order.status,
            "created_at": order.created_at.isoformat(),
            "items": enriched_items,
            "delivered": order.delivered,
            "paid": order.paid,
            "amount": order.amount
        }

        
        if role == "farmer":
            order_info.update({
                "customer_email": user_info.get("email"),
                "customer_username": user_info.get("username"),
                "customer_picture": user_info.get("profile_picture")
            })

        enriched_orders.append(order_info)

    return jsonify(enriched_orders), 200




@Order_bp.route('/Delivered', methods=['GET'])
@jwt_required()
def delivered_orders():
    verify_jwt_in_request()
    user_id = get_jwt_identity()
    role = get_jwt().get('role')

    delivered_param = request.args.get('delivered', 'false').lower()
    is_delivered = delivered_param == 'true'

    query = Order.query.filter(Order.delivered == is_delivered).order_by(Order.created_at.desc())

    if role == 'user':
        query = query.filter(Order.user_id == user_id)
    elif role == 'farmer':
        query = query.filter(Order.items.any(
            OrderItem.animal.has(Animal.farmer_id == user_id)
        ))

    results = query.all()

    if not results:
        return jsonify([{
            'error': 'No delivered orders' if is_delivered else 'No undelivered orders'
        }]), 404

    enriched_orders = []
    for order in results:
        enriched_items = []

        
        if role == 'farmer':
            customer_info = get_user_contact(order.user_id) or {}
        else:
            customer_info = {}

        for item in order.items:
            animal = Animal.query.get(item.animal_id)
            if not animal:
                continue

            
            if role == 'user':
                contact_info = get_farmer_contact(animal.farmer_id) or {}
            else:
                contact_info = {}

            enriched_items.append({
                "animal_id": animal.id,
                "name": animal.name,
                "type": animal.type,
                "breed": animal.breed,
                "age": animal.age,
                "price": animal.price,
                "description": animal.description,
                "is_available": animal.is_available,
                "image_count": len(animal.images),
                "quantity": item.quantity,
                "price_at_order_time": item.price_at_order_time,
                **({"farmer_email": contact_info.get("email"),
                    "farmer_username": contact_info.get("username"),
                    "farmer_picture": contact_info.get("profile_picture")} if role == "user" else {})
            })

        enriched_orders.append({
            "id": order.id,
            "user_id": order.user_id,
            "status": order.status,
            "delivered": order.delivered,
            "created_at": order.created_at,
            "items": enriched_items,
            **({"customer_email": customer_info.get("email"),
                "customer_username": customer_info.get("username"),
                "customer_picture": customer_info.get("profile_picture")} if role == "farmer" else {})
        })

    return jsonify(enriched_orders), 200


@Order_bp.route('/paid', methods=['GET'])
@jwt_required()
def get_paid_orders():
    verify_jwt_in_request()
    user_id = get_jwt_identity()
    role = get_jwt()['role']
    paid_param = request.args.get('paid', 'false').lower()

    is_paid = paid_param == 'true'

    query = Order.query.filter(Order.paid == is_paid).order_by(Order.created_at.desc())

    if role == 'user':
        query = query.filter(Order.user_id == user_id)
    elif role == 'farmer':
        query = query.filter(
            Order.items.any(
                OrderItem.animal.has(Animal.farmer_id == user_id)
            )
        )

    results = query.all()

    if not results:
        return jsonify([{
            'error': 'No paid orders' if is_paid else 'No unpaid orders'
        }]), 404

    enriched_orders = []
    for order in results:
        enriched_items = []

        
        if role == 'farmer':
            customer_info = get_user_contact(order.user_id) or {}
        else:
            customer_info = {}

        for item in order.items:
            animal = Animal.query.get(item.animal_id)
            if not animal:
                continue

            
            if role == 'user':
                farmer_info = get_farmer_contact(animal.farmer_id) or {}
            else:
                farmer_info = {}

            enriched_items.append({
                "animal_id": animal.id,
                "name": animal.name,
                "type": animal.type,
                "breed": animal.breed,
                "age": animal.age,
                "price": animal.price,
                "description": animal.description,
                "is_available": animal.is_available,
                "image_count": len(animal.images),
                "quantity": item.quantity,
                "price_at_order_time": item.price_at_order_time,
                **({
                    "farmer_email": farmer_info.get("email"),
                    "farmer_username": farmer_info.get("username"),
                    "farmer_picture": farmer_info.get("profile_picture")
                } if role == "user" else {})
            })

        enriched_orders.append({
            "id": order.id,
            "user_id": order.user_id,
            "status": order.status,
            "paid": order.paid,
            "created_at": order.created_at,
            "items": enriched_items,
            **({
                "customer_email": customer_info.get("email"),
                "customer_username": customer_info.get("username"),
                "customer_picture": customer_info.get("profile_picture")
            } if role == "farmer" else {})
        })

    return jsonify(enriched_orders), 200



@Order_bp.route('/Status', methods=['PUT'])
@role_required('farmer')
def status_update():
    verify_jwt_in_request()
    new_status = request.args.get('status', '').strip().lower()
    if new_status not in ['pending', 'confirmed', 'rejected']:
        return jsonify({'error': 'Invalid status value'}), 400

   
    order_data = request.get_json()
    if not order_data or 'id' not in order_data:
        return jsonify({'error': 'Order ID is required'}), 400

    order_id = order_data['id']
    order = Order.query.filter_by(id=order_id).first()
    if not order:
        return jsonify({'error': 'Order not found'}), 404

   
    order.status = new_status
    db.session.commit()

   
    updated_order = Order.query.filter_by(id=order_id).first()
    payload = OrderSchema().dump(updated_order)
    payload['status'] = new_status  

    try:
        from App.Utils.status_email_senders import (
            send_status_update_to_user,
            send_status_update_to_farmers
        )

        user_success, user_msg = send_status_update_to_user(payload)
        farmer_success, farmer_msg = send_status_update_to_farmers(payload)

        if user_success and farmer_success:
            return jsonify({'success': 'Emails sent to both user and farmers'}), 200
        elif not user_success and not farmer_success:
            return jsonify({'error': 'Failed to send emails to both user and farmers'}), 500
        elif not user_success:
            return jsonify({'error': f'User email failed: {user_msg}'}), 500
        else:
            return jsonify({'error': f'Farmer emails failed: {farmer_msg}'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@Order_bp.route('/DeliveryStatus/<string:orderid>', methods=['PUT'])
@jwt_required()
@role_required('customer')
def delivery_status_update(orderid):
    verify_jwt_in_request()
    user_id = get_jwt_identity()
    from App.Utils.Delivery_email_senders import send_delivery_email_to_user, send_delivery_email_to_farmers
    delivered = request.args.get('delivered', 'false').lower() == 'true'
    order = Order.query.filter_by(id=orderid, user_id=user_id).first()

    if not order:
        return jsonify({'error': 'Order not found'}), 404

    order.delivered = delivered
    db.session.commit()

    order_data = {
        'id': order.id,
        'user_id': order.user_id,
        'items': [{
            'id': item.id,
            'animal_id': item.animal_id,
            'quantity': item.quantity,
            'price_at_order_time': str(item.price_at_order_time)
        } for item in order.items]
    }

    if delivered:
        user_success = send_delivery_email_to_user(order.user_id, order_data['items'])
        farmer_failures = send_delivery_email_to_farmers(order_data['items'])

        if not user_success:
            return jsonify({'error': 'Failed to send delivery email to user'}), 500
        if farmer_failures:
            return jsonify({'error': 'Failed to send email to some farmers', 'failed_emails': farmer_failures}), 500

    return jsonify(order_data), 200

@Order_bp.route('/PaymentStatus/<string:orderid>', methods=['PUT'])
@jwt_required()
def payment_status_update(orderid):
    verify_jwt_in_request()
    from App.Utils.Payment_email_senders import  send_payment_confirmation_to_user, send_payment_confirmation_to_farmers
    user_id = get_jwt_identity()

    paid = request.args.get('paid', 'false').lower() == 'true'

    order = Order.query.filter_by(user_id=user_id, id=orderid).first()
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    order.paid = paid
    db.session.commit()

    order_data = {
        'id': order.id,
        'user_id': order.user_id,
        'status': order.status,
        'paid': order.paid,
        'delivered': order.delivered,
        'amount': str(order.amount),
        'created_at': order.created_at.isoformat(),
        'items': [
            {
                'id': item.id,
                'order_id': item.order_id,
                'animal_id': item.animal_id,
                'quantity': item.quantity,
                'price_at_order_time': str(item.price_at_order_time)
            }
            for item in order.items
        ]
    }
    items = order_data['items']

    if paid:
        try:
            from App.Utils.mail_utils import group_items_by_farmer_util

            farmers = group_items_by_farmer_util(items)
            payment_method = request.args.get("method", "card") 

            send_payment_confirmation_to_farmers(farmers, payment_method)
            send_payment_confirmation_to_user(user_id, order_data)

        except Exception as e:
            print(f"Email sending failed: {e}")
            return jsonify({'error': 'Failed to send confirmation emails'}), 500

        return jsonify({'message': "Payment confirmation emails sent successfully"}), 200

    return jsonify(order_data), 200


@Order_bp.route('/delete/<string:order_id>', methods=['DELETE'])
@jwt_required()
def delete_order(order_id):
    verify_jwt_in_request()
    user_id = get_jwt_identity()
    role = get_jwt()['role']

    order = Order.query.get(order_id)

    if not order:
        return jsonify({'error': 'Order not found'}), 404

    
    if role == 'user' and order.user_id != user_id:
        return jsonify({'error': 'Unauthorized to delete this order'}), 403
    if role == 'farmer':
        return jsonify({'error': 'Farmers cannot delete orders'}), 403

    try:
        db.session.delete(order)
        db.session.commit()
        return jsonify({'message': 'Order deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete order', 'details': str(e)}), 500

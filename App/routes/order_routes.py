from flask import Blueprint, request, jsonify, Response
from App.services.Order_services import OrderService
from App.Schema.Order_schema import OrderSchema
from decimal import Decimal
from App.models.Orders import Order, OrderItem
import requests
from App.extensions import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from App.Utils.Order_email_senders import send_order_confirmation_to_user, send_order_confirmation_to_farmers
from functools import wraps
from App.Utils.mail_utils import group_items_by_farmer_util_for_user, group_items_by_farmer_util_for_farmer, get_farmer_contact


Order_bp = Blueprint('Order_bp', __name__)


def get_jwt_role():
    jwt_data = get_jwt()
    return jwt_data.get("role") 


def role_required(*required_roles):
    def wrapper(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
            except Exception as e:
                return jsonify({"error": "Token missing or invalid", "details": str(e)}), 401

            user_role = claims.get('role')
            if user_role not in required_roles:
                return jsonify({"error": "Access denied: insufficient permissions"}), 403

            return fn(*args, **kwargs)
        return wrapped
    return wrapper

@Order_bp.route('/create', methods=['POST'])
@jwt_required()
@role_required('customer')
def create_order():
    order_service = OrderService()
    data = request.get_json()

    if not data:
        return jsonify([{'error': 'Missing request body'}]), 400

    user_id = get_jwt_identity()
    amount = data['amount']
    items = data['items']

    if not user_id:
        return jsonify([{'error': 'Missing user_id'}]), 400
    if not amount:
        return jsonify([{'error': 'Missing order amount'}]), 400
    if not items or not isinstance(items, list):
        return jsonify([{'error': 'Invalid or empty items list'}]), 400

    order, status = order_service.create_order(user_id, amount)
    if status != 201:
        return order, status

    for item in items:
        animal_id = item.get('animal_id')
        quantity = item.get('quantity')
        price = item.get('price_at_order_time')

        if not all([animal_id, quantity, price]):
            continue

        result, item_status = order_service.create_order_Item(order.id, animal_id, quantity, price)
        if item_status != 201:
            return result, item_status  

    payload = {
        'id': order.id,
        'created_at': str(order.created_at),
        'amount': str(order.amount),
        'items': items
    }

   
    user_mail_success, user_error = send_order_confirmation_to_user(
        user_id=user_id,
        order_id=order.id,
        created_at=str(order.created_at),
        amount=str(order.amount),
        items=items
    )

    if not user_mail_success:
        print(f"User email failed: {user_error}")

    successful, failed = send_order_confirmation_to_farmers(items)
    if failed:
        print("Some farmer emails failed:", failed)

    return jsonify(OrderSchema().dump(order)), 201



@Order_bp.route('/all', methods=['GET'])
@jwt_required()
@role_required("farmer", "customer")
def past_orders():
    id = get_jwt_identity()
    role = get_jwt_role()  

    orders = Order.query.filter_by(user_id=id).order_by(Order.created_at.desc()).all()
    if not orders:
        return jsonify([{'error': 'empty order history'}]), 404

    full_orders = []
    for order in orders:
        items = [
            {
                "animal_id": item.animal_id,
                "quantity": item.quantity,
                "price_at_order_time": float(item.price_at_order_time)
            } for item in order.items
        ]

        if role == "customer":
            enriched_animals = group_items_by_farmer_util_for_user(items)
        elif role == "farmer":
            enriched_animals = group_items_by_farmer_util_for_farmer(user_id=id, items=items)
        else:
            enriched_animals = []

        full_orders.append({
            "id": order.id,
            "status": order.status,
            "paid": order.paid,
            "delivered": order.delivered,
            "amount": float(order.amount),
            "pickup_station": order.pickup_station,
            "payment_method": order.payment_method,
            "created_at": order.created_at.isoformat(),
            "animals": enriched_animals
        })

    return jsonify(full_orders), 200

@Order_bp.route('/<string:order_id>', methods=['GET'])
@jwt_required()
@role_required("farmer", "customer")
def get_order_by_id(order_id):
    user_id = get_jwt_identity()
    role = g.current_role

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


    if role == 'customer':
        enriched_animals = group_items_by_farmer_util_for_user(item_dicts)
    else:  
        enriched_animals = group_items_by_farmer_util_for_farmer(user_id, item_dicts)

        
        if not enriched_animals:
            return jsonify({'error': 'Access denied'}), 403


    order_data = OrderSchema().dump(order)
    order_data['animals'] = enriched_animals

    return jsonify(order_data), 200



@Order_bp.route('/status', methods=['GET'])
@jwt_required()
def get_orders_by_status():
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

        for item in order.items:
            animal = Animal.query.get(item.animal_id)
            if not animal:
                continue

            farmer_info = get_farmer_contact(animal.farmer_id) or {}

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
                "farmer_email": farmer_info.get("email"),
                "farmer_username": farmer_info.get("username"),
            })

        enriched_orders.append({
            "id": order.id,
            "user_id": order.user_id,
            "status": order.status,
            "created_at": order.created_at,
            "items": enriched_items
        })

    return jsonify(enriched_orders), 200



@Order_bp.route('/Delivered', methods=['GET'])
@jwt_required()
def delivered_orders():
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

        for item in order.items:
            animal = Animal.query.get(item.animal_id)
            if not animal:
                continue

            farmer_info = get_farmer_contact(animal.farmer_id) or {}

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
                "farmer_email": farmer_info.get("email"),
                "farmer_username": farmer_info.get("username"),
            })

        enriched_orders.append({
            "id": order.id,
            "user_id": order.user_id,
            "status": order.status,
            "delivered": order.delivered,
            "created_at": order.created_at,
            "items": enriched_items
        })

    return jsonify(enriched_orders), 200



@Order_bp.route('/paid', methods=['GET'])
@jwt_required()
def get_paid_orders():
    user_id = get_jwt_identity()
    role = get_jwt()['role']
    paid_param = request.args.get('paid', 'false').lower()

    is_paid = paid_param == 'true'

    query = Order.query.filter(Order.paid == is_paid).order_by(Order.created_at.desc())

    # Role-specific filtering
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

        for item in order.items:
            animal = Animal.query.get(item.animal_id)
            if not animal:
                continue

            farmer_info = get_farmer_contact(animal.farmer_id) or {}

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
                "farmer_email": farmer_info.get("email"),
                "farmer_username": farmer_info.get("username"),
            })

        enriched_orders.append({
            "id": order.id,
            "user_id": order.user_id,
            "status": order.status,
            "paid": order.paid,
            "created_at": order.created_at,
            "items": enriched_items
        })

    return jsonify(enriched_orders), 200



@Order_bp.route('/Status', methods=['PUT'])
@role_required('farmer')
def status_update():
    
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
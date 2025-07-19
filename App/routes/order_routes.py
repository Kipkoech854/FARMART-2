from flask import Blueprint, request, jsonify, Response
from App.services.Order_services import OrderService
from App.Schema.Order_schema import OrderSchema
from decimal import Decimal
from App.models.Orders import Order, OrderItem
import requests
from App.extensions import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from App.Utils.Order_email_senders import send_order_confirmation_to_user, send_order_confirmation_to_farmers

Order_bp = Blueprint('Order_bp', __name__)

@Order_bp.route('/create', methods=['POST'])
@jwt_required()
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



@Order_bp.route('/all/<string:id>', methods=['GET'])
def past_orders(id):
    results = Order.query.filter_by(user_id=id).order_by(Order.created_at.desc()).all()

    if not results:
        return jsonify([{'error': 'empty order history'}]), 404

    return jsonify(OrderSchema(many=True).dump(results)), 200

@Order_bp.route('/pending/<string:id>', methods=['GET'])
def pending_orders(id):
    results = Order.query.filter(
        Order.user_id.like(f'%{id}%'),
        Order.status.ilike('%pending%')
    ).order_by(Order.created_at.desc()).all()

    if not results:
        return jsonify([{'error': 'No pending orders available'}]), 404

    return jsonify(OrderSchema(many=True).dump(results)), 200

@Order_bp.route('/Confirmed/<string:id>', methods=['GET'])
def confirmed_orders(id):
    results = Order.query.filter(
        Order.user_id.like(f'%{id}%'),
        Order.status.ilike('%confirmed%')
    ).order_by(Order.created_at.desc()).all()

    if not results:
        return jsonify([{'error': 'No pending orders available'}]), 404

    return jsonify(OrderSchema(many=True).dump(results)), 200




@Order_bp.route('/Delivered/<string:id>', methods=['GET'])
def delivered_orders(id):
    delivered = request.args.get('delivered', 'false').lower()

    
    is_delivered = delivered == 'true'
    

    results = Order.query.filter_by(user_id=id, delivered=is_delivered).order_by(Order.created_at.desc()).all()

    if not results:
        return jsonify([{
            'error': 'no delivered orders' if is_delivered else 'no undelivered orders'
        }]), 404

    return jsonify(OrderSchema(many=True).dump(results)), 200


@Order_bp.route('/Paid/<string:id>', methods=['GET'])
def Paid_orders(id):
    paid = request.args.get('paid', 'false').lower()

    
    is_paid = paid == 'true'
    

    results = Order.query.filter_by(user_id=id, paid=is_paid).order_by(Order.created_at.desc()).all()

    if not results:
        return jsonify([{
            'error': 'no paid orders' if is_paid else 'no unpaid orders'
        }]), 404

    return jsonify(OrderSchema(many=True).dump(results)), 200


@Order_bp.route('/Status', methods=['PUT'])
def status_update():
    # 1. Get new status from query param
    new_status = request.args.get('status', 'pending').lower()
    if new_status not in ['pending', 'confirmed', 'rejected']:
        return jsonify({'error': 'Invalid status value'}), 400

    # 2. Get full order JSON from request body
    order_data = request.get_json()
    if not order_data:
        return jsonify({'error': 'Missing order data'}), 400

    order_id = order_data.get('id')
    if not order_id:
        return jsonify({'error': 'Order ID is required'}), 400

    # 3. Query order by ID
    order = Order.query.filter_by(id=order_id).first()
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    # 4. Update status only
    order.status = new_status
    db.session.commit()

    # 5. Re-query to get fresh data (eager load items if needed)
    updated_order = Order.query.filter_by(id=order_id).first()

    # 6. Serialize order with nested items
    payload = OrderSchema().dump(updated_order)
    if payload:
        user_email_success = False
        farmer_email_success = False
        try:
            response = requests.post(
                'http://127.0.0.1:5555/api/StatusMail/Status-Changed-User',
                json=payload
                )
            user_email_success = response.status_code == 200
                
            res = requests.post(
                'http://127.0.0.1:5555/api/StatusMail/Status-Changed-Farmer',
                json=payload
                )
            farmer_email_success = res.status_code == 200
            if user_email_success and farmer_email_success:
                print("Emails sent to farmers and users")
                return jsonify({'success': 'Emails sent to farmers and users'}), 200
                    
            elif not user_email_success and not farmer_email_success:
                return jsonify({'error': 'Failed to send email to both user and farmers'}), 500
                    
            elif not user_email_success:
                return jsonify({'error': 'Failed to send email to user'}), 500
                    
            elif not farmer_email_success:
                return jsonify({'error': 'Failed to send email to farmers'}), 500

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # 7. Return full updated order
    return jsonify(payload), 200


@Order_bp.route('/DeliveryStatus/<string:orderid>', methods=['PUT'])
@jwt_required()
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
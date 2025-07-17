from flask import Blueprint, request, jsonify
from App.services.Order_services import OrderService
from App.Schema.Order_schema import OrderSchema
from decimal import Decimal
from App.models.Orders import Order, OrderItem
import requests
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity


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

    try:
        User_mail_response = requests.post(
            f'http://127.0.0.1:5555/api/Mail/Order-User/{user_id}',
            json=payload
        )
        if User_mail_response.status_code != 200:
            print("Mail service error:", User_mail_response.text)
        
        farmer_mail_response = requests.post(
            f'http://127.0.0.1:5555/api/Mail/Order-farmer',
            json=payload
        )
        if farmer_mail_response.status_code != 200:
            print('Mail servive eror:', farmer_mail_response.text)
    except Exception as e:
        print("Mail request failed:", e)

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

@Order_bp.route('/Status/<string:userid>/<string:orderid>', methods=['PUT'])
def status_update(userid, orderid):
    order_service = OrderService()
    status = request.args.get('status', 'pending').lower()

    if status not in ['pending', 'confirmed', 'rejected']:
        return jsonify([{'error': 'Invalid status value'}]), 400

    return order_service.update_status(user_id=userid, order_id=orderid, status=status)

@Order_bp.route('/DeliveryStatus/<string:userid>/<string:orderid>', methods=['PUT'])
def delivery_status_update(userid, orderid):
    order_service = OrderService()
    delivered = request.args.get('delivered', 'false').lower() == 'true'

    return order_service.update_delivered(user_id=userid, order_id=orderid, delivered=delivered)

@Order_bp.route('/PaymentStatus/<string:userid>/<string:orderid>', methods=['PUT'])
def payment_status_update(userid, orderid):
    order_service = OrderService()
    paid = request.args.get('paid', 'false').lower() == 'true'

    return order_service.update_paid(user_id=userid, order_id=orderid, paid=paid)    

from flask import Blueprint, request, jsonify
from App.services.Order_services import OrderService
from App.Schema.Order_schema import OrderSchema
from decimal import Decimal

Order_bp = Blueprint('Order_bp', __name__)

@Order_bp.route('/create', methods=['POST'])
def create_order():
    order_service = OrderService()
    data = request.get_json()
    

    if not data:
        return jsonify([{'error': 'Missing request body'}]), 400

    user_id = data.get('user_id')
    amount = data.get('amount')
    items = data.get('items')

   
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

        order_service.create_order_item(order.id, animal_id, quantity, price)

    return jsonify(OrderSchema().dump(order)), 201

@Order_bp.route('/debug-db', methods=['GET'])
def debug_db():
    from flask import current_app
    from App.extensions import db

    if not current_app:
        return jsonify({'error': 'No app context'}), 500

    try:
        with current_app.app_context():
            db.engine.execute("SELECT 1")
            return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

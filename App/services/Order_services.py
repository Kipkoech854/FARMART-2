from flask import Flask, jsonify
from App.Schema.Order_schema import OrderItemSchema, OrderSchema
from App.models.Orders import Order, OrderItem
from App.extensions import db
from decimal import Decimal


class OrderService:
    def __init__(self):
        pass

    
    def create_order(user_id, amount, delivery_method, pickup_station, payment_method, total):
        new_order = Order(
            user_id=user_id,
            amount=amount,
            delivery_method=delivery_method,
            pickup_station=pickup_station,
            payment_method=payment_method,
            total=total
        )
        db.session.add(new_order)
        db.session.commit()
        return new_order


   
    @staticmethod
    def create_order_Item(order_id, animal_id, quantity, price_at_order_time, farmer_id):
        """Creating a new order item instance"""
        try:
            if not isinstance(price_at_order_time, Decimal):
                price_at_order_time = Decimal(str(price_at_order_time))

            new_item = OrderItem(
                order_id=order_id,
                animal_id=animal_id,
                quantity=quantity,
                price_at_order_time=price_at_order_time,
                farmer_id=farmer_id
            )

            db.session.add(new_item)
            db.session.commit()

            return new_item, 201

        except Exception as e:
            db.session.rollback()
            return jsonify([{"error": str(e)}]), 500


    def update_status(self, user_id, order_id, status):
        try:
            order = Order.query.filter_by(user_id=user_id, id=order_id).first()

            if not order:
                return jsonify([{'error': 'No order found for this user'}]), 404

            order.status = status
            db.session.commit()

            return jsonify({
                'message': 'Order status updated successfully',
                'order': OrderSchema().dump(order)
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify([{'error': str(e)}]), 500


    def update_delivered(self, user_id, order_id, delivered):
        """Updating delivery status"""
        try:
            order = Order.query.filter_by(user_id=user_id, id=order_id).first()

            if not order:
                return jsonify([{'error': 'No order found for this user'}]), 404

            order.delivered = delivered
            db.session.commit()

            return jsonify({
                'message': 'Delivery status updated successfully',
                'order': OrderSchema().dump(order)
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify([{'error': str(e)}]), 500
       
    
    def update_paid(self, user_id,order_id, paid):
        """Update the most recent unpaid order's payment status for a specific user"""
        try:
        
            order = Order.query.filter_by(user_id=user_id,id = order_id, paid=False).order_by(Order.created_at.desc()).first()

            if not order:
                return jsonify([{'error': 'No unpaid order found for this user'}]), 404

            order.paid = paid
            db.session.commit()

            return jsonify({
                'message': 'Payment status updated successfully',
                'order':OrderSchema().dump(order)
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify([{'error': str(e)}]), 500

from flask import Flask, jsonify
from App.Schema.Order_schema import OrderItemSchema, OrderSchema
from App.models.Orders import Order, OrderItem
from App.extensions import db
from decimal import Decimal


class OrderService:
    def __init__(self):
        pass

    def create_order(self, user_id, amount):
        """Creating a new order"""
        try:
            if not isinstance(amount, Decimal):
                amount = Decimal(str(amount))

            new_order = Order(user_id=user_id, amount=amount)  # use model class here

            db.session.add(new_order)
            db.session.commit()

            print('new order created!')
            return new_order, 201

        except Exception as e:
            db.session.rollback()
            return jsonify([{'DatabaseError': str(e)}]), 500

    def create_order_Item(self, order_id, animal_id, quantity, price_at_order_time):
        """Creating a new order item instance"""
        try:
            if not isinstance(price_at_order_time, Decimal):
                price_at_order_time = Decimal(str(price_at_order_time))

            new_item = OrderItem(
                order_id=order_id,
                animal_id=animal_id,
                quantity=quantity,
                price_at_order_time=price_at_order_time
            )

            db.session.add(new_item)
            db.session.commit()

            return new_item, 201

        except Exception as e:
            db.session.rollback()
            return jsonify([{"error": str(e)}]), 500

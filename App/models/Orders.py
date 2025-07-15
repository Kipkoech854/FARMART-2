from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime  

db = SQLAlchemy()
ma = Marshmallow()

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("OrderItem", backref="order", cascade="all, delete-orphan")


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    animal_id = db.Column(db.Integer, db.ForeignKey('animals.id'))
    quantity = db.Column(db.Integer, default=1)
    price_at_order_time = db.Column(db.Float)


class OrderItemSchema(ma.SQLAlchemySchema):
    class Meta:
        model = OrderItem
        include_fk = True

    id = ma.auto_field()
    order_id = ma.auto_field()
    animal_id = ma.auto_field()
    quantity = ma.auto_field()
    price_at_order_time = ma.auto_field()


class OrderSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Order
        include_fk = True

    id = ma.auto_field()
    user_id = ma.auto_field()
    status = ma.auto_field()
    created_at = ma.auto_field()
    
    items = ma.Nested(OrderItemSchema, many=True) 
from App import db
from flask import Flask
from sqlalchemy import Numeric
from datetime import datetime 
import uuid 
from App.extensions import db


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String, db.ForeignKey('users.id'))
    status = db.Column(db.String(50), default='Pending')
    paid = db.Column(db.Boolean, default = False)
    delivered = db.Column(db.Boolean, default = False)
    amount = db.Column(Numeric(10,2), nullable = False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


    items = db.relationship("OrderItem", backref="order", cascade="all, delete-orphan")


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.String, db.ForeignKey('orders.id'))
    animal_id = db.Column(db.String, db.ForeignKey('animals.id'))
    quantity = db.Column(db.Integer, default=1)
    price_at_order_time = db.Column(Numeric(10,2), nullable = False)






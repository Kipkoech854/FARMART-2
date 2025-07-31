from App.extensions import db
from sqlalchemy.dialects.postgresql import UUID, NUMERIC
from datetime import datetime
import uuid

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    status = db.Column(db.String(50), default='Pending')
    paid = db.Column(db.Boolean, default=False)
    delivered = db.Column(db.Boolean, default=False)
    amount = db.Column(NUMERIC(10, 2), nullable=False)
    pickup_station = db.Column(db.String, nullable=True)
    payment_method = db.Column(db.String, default='cash')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    delivery_method = db.Column(db.String, nullable=False)
    total = db.Column(db.Float, nullable=False)

    items = db.relationship(
        "OrderItem",
        backref="order",  # ✅ no name conflict now
        cascade="all, delete-orphan",
        passive_deletes=True
    )



class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = db.Column(UUID(as_uuid=True), db.ForeignKey('orders.id'), nullable=False)
    animal_id = db.Column(UUID(as_uuid=True), db.ForeignKey('animals.id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(UUID(as_uuid=True), nullable=False)
    price_at_order_time = db.Column(NUMERIC(10, 2), nullable=False)

    farmer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('farmers.id'), nullable=False)

    farmer = db.relationship("Farmer", backref="order_items")
    animal = db.relationship("Animal", backref="order_items")

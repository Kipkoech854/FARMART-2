from App.extensions import db
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False) 
    amount = db.Column(db.Integer, nullable=False)
    shipping_cost = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    pickup_location = db.Column(db.String, nullable=False)
    shipping_method = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('Item', backref='payment', lazy=True)
    
    @property
    def computed_total(self):
        return self.amount + self.shipping_cost


class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_id = db.Column(UUID(as_uuid=True), db.ForeignKey('payments.id'), nullable=False)
    item_id = db.Column(UUID(as_uuid=True), db.ForeignKey('animals.id'), nullable=False)

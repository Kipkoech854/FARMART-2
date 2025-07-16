from flask import Flask
from App.extensions import ma
from App.models.Orders import Order, OrderItem



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

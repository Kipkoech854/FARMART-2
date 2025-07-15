from flask import Flask
from App.models.Orders import OrderItemSchema, OrderSchema

order = OrderSchema()
orderitem = OrderItemSchema()

class Order:
    def __init__(self):
        

    def create_order(data:dict):
        """ Creating a new order"""

        try:
            order_data = order.load(data)

            new_order = Order(**order_data)

            db.session.add(new_order)
            db.session.commit()
            
            print ('new order created!')
            return jsonify(new_order), 200

        except Exception as e:
            db.session.rollback()
            return jsonify([{'DatabaseError':str(e)}]), 500     

        

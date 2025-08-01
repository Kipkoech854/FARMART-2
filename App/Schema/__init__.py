from flask import Flask
from flask_marshmallow import Marshmallow

ma = Marshmallow()

from .Users_schema import UserSchema
from .Animal_schema import AnimalSchema, AnimalImageSchema
from .Farmer_schema import FarmersSchema
from .Feedback_schema import FeedbackSchema
from .Order_schema import OrderSchema, OrderItemSchema


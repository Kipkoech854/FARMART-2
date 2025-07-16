from flask import Flask
from flask_marshmallow import Marshmallow

ma = Marshmallow()

from .Users_schema import UserSchema
from .Animal_schema import AnimalSchema, AnimalimagesSchema
from .Farmer_schema import FarmersSchema
from .Feedback_schema import FeedbackSchema
from Order_Schema import OrderSchema, OrderItemSchema

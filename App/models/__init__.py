from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()


from .Users import User
from .Feedback import Feedback
from .Orders import Order, OrderItem
from .Animals import Animal, Animalimages
from .Farmers import Farmers




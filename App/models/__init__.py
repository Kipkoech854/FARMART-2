from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()

from .Animals import Animal,Animalimages
from .Farmers import Farmers
from .Order import Order, OrderItem
from .Feedback import Feedback
from .Users import User
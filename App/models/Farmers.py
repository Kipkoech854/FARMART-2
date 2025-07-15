from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()

class Farmers(db.Model):
    __tablename__ = 'farmers'

    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.Integer, nullable=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    profile_picture = db.Column(db.String(255))


class FarmersSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Farmers  

    id = ma.auto_field()
    email = ma.auto_field()
    phone = ma.auto_field()
    username = ma.auto_field()
    password = ma.auto_field()
    profile_picture = ma.auto_field()

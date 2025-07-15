from  flask  import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()
ma = Marshmallow()

class Animal(db.Model):
    __tablename__ = 'animals'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    breed = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    is_available = db.Column(db.Boolean, default=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    images = db.relationship("Animalimages", backref="animal", lazy=True)


class Animalimages(db.Model):

    __tablename__ = 'animal_images'

    id = db.Column(db.Integer, primary_key = True)
    url = db.Column(db.String(255), nullable = False)
    animal_id =db.Column(db.Integer, db.ForeignKey('animals.id'), nullable = False)

   
class AnimalSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Animal
        include_fk = True

    id = ma.auto_field()
    name = ma.auto_field()
    type = ma.auto_field()
    breed = ma. auto_field()
    age = ma.auto_field()
    price = ma.auto_field()
    description = ma.auto_field()
    is_available = ma.auto_field()
    farmer_id = ma.auto_field()

    images = ma.Nested('AnimalimagesSchema', many=True)              

class AnimalimagesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Animalimages
        include_fk = True

    id = ma.auto_field()
    url = ma.auto_field()
    animal_id = ma.auto_field()  

   
from flask import Flask
from App.extensions import ma
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from App.models.Animals import Animal,AnimalImages



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
        model = AnimalImages
        include_fk = True

    id = ma.auto_field()
    url = ma.auto_field()
    animal_id = ma.auto_field()  

   
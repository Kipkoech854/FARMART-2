from flask import Flask
from App.extensions import ma
from App.models.Farmers import Farmer

from App.Schema.Animal_schema import AnimalSchema  

class FarmersSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Farmer
        load_instance = True

    id = ma.auto_field()
    email = ma.auto_field()
    phone = ma.auto_field()
    username = ma.auto_field()
    profile_picture = ma.auto_field()
    verified = ma.auto_field()
    
    
    animals = ma.Nested(AnimalSchema, many=True)

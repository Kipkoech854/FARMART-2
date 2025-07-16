from flask import Flask
from App.extensions import ma
from App.models.Farmers import Farmers



class FarmersSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Farmers  

    id = ma.auto_field()
    email = ma.auto_field()
    phone = ma.auto_field()
    username = ma.auto_field()
    password = ma.auto_field()
    profile_picture = ma.auto_field()

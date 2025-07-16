from App.extensions import ma
from App.models.Users import User



class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        load_instance = True 

    id = ma.auto_field()
    username = ma.auto_field()
    email = ma.auto_field()
    password = ma.auto_field()
    role = ma.auto_field()
    profile_picture = ma.auto_field()

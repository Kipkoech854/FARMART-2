from App.extensions import ma
from .Users_schema import  UserSchema
from App.models.Feedback import Feedback



class FeedbackSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Feedback
        include_fk = True
        load_instance = True

    id = ma.auto_field()
    user_id = ma.auto_field()
    farmer_id = ma.auto_field()
    rating = ma.auto_field()
    comment = ma.auto_field()
    image_url = ma.auto_field()
    
    
    user = ma.Nested(UserSchema, only=("id", "username", "profile_picture"))
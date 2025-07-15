from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from .Users import User

db = SQLAlchemy()
ma = Marshmallow()


class Feedback(db.Model):

    __tablename__ = 'feedback'

    id = db.Column(db.String, primary_key = True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable = False)
    farmer_id = db.Column(db.String, db.ForeignKey('farmers.id'), nullable = False)
    rating = db.Column(db.Integer, nullable = False)
    comment = db.Column(db.String, nullable = True)
    image_url = db.Column(db.String(255))

    user = db.relationship("User", backref="feedbacks")

class FeedbackSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Feedback
        include_fk = True

    id = ma.auto_field()
    user_id = ma.auto_field()
    farmer_id = ma.auto_field()
    rating = ma.auto_field()
    comment = ma.auto_field()
    image_url = ma.auto_field()     

    user = ma.Nested("UserSchema", only=("id", "username", "profile_picture"))   
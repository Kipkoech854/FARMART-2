
from App import db

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()



class Feedback(db.Model):

    __tablename__ = 'feedback'

    id = db.Column(db.String, primary_key = True)
    user_id = db.Column(db.string, db.ForeignKey('users.id'), nullable = False)
    farmer_id = db.Column(db.String, db.ForeignKey('farmers.id'), nullable = False)
    rating = db.Column(db.Integer, nullable = False)
    comment = db.Column(db.String, nullable = True) 
    image_url = db.Column(db.String(255))


    user = db.relationship("User", back_populates="feedbacks")
    farmer = db.relationship("Farmers", back_populates="feedbacks")
    

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "farmer_id": self.farmer_id,
            "rating": self.rating,
            "comment": self.comment,
            "image_url": self.image_url
        }


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


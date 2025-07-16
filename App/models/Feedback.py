
from flask_marshmallow import Marshmallow
from App.models.Users import User
from App.extensions import db
from App.models.Users import User 



class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    farmer_id = db.Column(db.String, db.ForeignKey('farmers.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String, nullable=True)
    image_url = db.Column(db.String(255))

   



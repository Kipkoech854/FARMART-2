from App.extensions import db, ma
from App.models.Users import User
from App.models.Farmers import Farmer
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Feedback(db.Model):
    __tablename__ = 'feedback'
animal-variation
    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    farmer_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String, nullable=True)
    image_url = db.Column(db.String(255))
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='feedback_given')
    farmer = db.relationship('User', foreign_keys=[farmer_id], backref='feedback_re

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String, nullable=True)
    image_url = db.Column(db.String(255))

  
    user = db.relationship("User", back_populates="feedbacks")
    farmer = db.relationship("Farmer", back_populates="feedbacks")


    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "farmer_id": self.farmer_id,
            "rating": self.rating,
            "comment": self.comment,
            "image_url": self.image_url
        }

    main

from App.extensions import db, ma
from App.models.Users import User
from App.models.Farmers import Farmer
import uuid

class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    farmer_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('farmers.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String, nullable=True)
    image_url = db.Column(db.String(255))

    # Relationships
    user = db.relationship("User", back_populates="feedbacks")
    farmer = db.relationship("Farmer", back_populates="feedbacks")

    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "farmer_id": str(self.farmer_id),
            "rating": self.rating,
            "comment": self.comment,
            "image_url": self.image_url
        }


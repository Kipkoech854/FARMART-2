from App import db


class Feedback(db.Model):

    __tablename__ = 'feedback'

    id = db.Column(db.String, primary_key = True)
    user_id = db.Column(db.string, db.ForeignKey('users.id'), nullable = False)
    farmer_id = db.Column(db.String, db.ForeignKey('farmers.id'), nullable = False)
    rating = db.Column(db.Integer, nullable = False)
    comment = db.Column(db.String, nullable = True)
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
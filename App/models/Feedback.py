from App.extensions import db

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    farmer_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String, nullable=True)
    image_url = db.Column(db.String(255))
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='feedback_given')
    farmer = db.relationship('User', foreign_keys=[farmer_id], backref='feedback_received')
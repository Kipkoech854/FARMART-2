from App.extensions import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String(120), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    profile_picture = db.Column(db.String(255), nullable=True)

    
    feedbacks = db.relationship("Feedback", back_populates="user", cascade="all, delete-orphan")

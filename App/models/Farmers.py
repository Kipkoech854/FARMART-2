from App.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Farmer(db.Model):
    __tablename__ = 'farmers'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    username = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    profile_picture = db.Column(db.String(255))
    verified = db.Column(db.String(20), default='unverified')
    role = db.Column(db.String(10), default='farmer')

    feedbacks = db.relationship("Feedback", back_populates="farmer", cascade="all, delete-orphan")
    animals = db.relationship('Animal', back_populates='farmer', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

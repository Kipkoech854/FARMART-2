from App.extensions import db, bcrypt
import uuid
from sqlalchemy.dialects.postgresql import UUID

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    profile_picture = db.Column(db.String(255), nullable=True)
    verified = db.Column(db.String(20), default='unverified')
    
    likes = db.relationship("Like", back_populates="user", cascade="all, delete-orphan")
    feedbacks = db.relationship("Feedback", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, plain_password):
        self.password = bcrypt.generate_password_hash(plain_password).decode("utf-8")

    def check_password(self, plain_password):
        return bcrypt.check_password_hash(self.password, plain_password)

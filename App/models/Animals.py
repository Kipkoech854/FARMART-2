from App.extensions import db
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Animal(db.Model):
    __tablename__ = 'animals'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    breed = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    is_available = db.Column(db.Boolean, default=True)
    location = db.Column(db.String, nullable = False)
    farmer_id = db.Column(db.String, db.ForeignKey('farmers.id', name='fk_animals_farmer_id_users'))

    images = db.relationship("AnimalImage", backref="animal", cascade="all, delete-orphan")
    likes = db.relationship("Like", back_populates="animal", cascade="all, delete-orphan")

class AnimalImage(db.Model):  
    __tablename__ = 'animal_images'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    url = db.Column(db.String(255), nullable=False)
    animal_id = db.Column(db.String(36), db.ForeignKey('animals.id'), nullable=False)


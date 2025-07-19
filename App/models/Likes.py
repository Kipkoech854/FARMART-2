from App.extensions import db
import uuid

class Like(db.Model):
    __tablename__ = 'likes'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    animal_id = db.Column(db.String(36), db.ForeignKey('animals.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

 
    user = db.relationship('User', back_populates='likes')
    animal = db.relationship('Animal', back_populates='likes')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'animal_id', name='unique_user_animal_like'),
    )

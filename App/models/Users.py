from App.extensions import db
from App.extensions import db, bcrypt

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    def set_password(self, plain_password):
        self.password = bcrypt.generate_password_hash(plain_password).decode("utf-8")

    def check_password(self, plain_password):
        return bcrypt.check_password_hash(self.password, plain_password)


    feedbacks = db.relationship("Feedback", backref="user", cascade="all, delete-orphan")

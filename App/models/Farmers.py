from App.extensions import db, bcrypt

class Farmer(db.Model):
    __tablename__ = 'farmers'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.Integer, nullable=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    profile_picture = db.Column(db.String(255))

    feedback = db.relationship("Feedback", backref="farmer", cascade="all, delete-orphan")

    def set_password(self, plain_password):
        self.password = bcrypt.generate_password_hash(plain_password).decode('utf-8')

    def check_password(self, plain_password):
        return bcrypt.check_password_hash(self.password, plain_password)

    
    feedback = db.relationship("Feedback", backref="farmer", cascade="all, delete-orphan")

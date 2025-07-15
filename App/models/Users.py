class User(db.Model):
    
    __tablename__ = 'users'

    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String(120), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    animals = db.relationship("Animal", backref="farmer", lazy=True)
    orders = db.relationship("Order", backref="user", lazy=True)
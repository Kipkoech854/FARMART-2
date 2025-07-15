class Animal(db.Model):
    __tablename__ = 'animals'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    breed = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    is_available = db.Column(db.Boolean, default=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class Animalimages(db.Model):

    __tablename__ = 'animal_images'

    id = db.Column(db.Integer, primary_key = True)
    url = db.Column(db.String(255), nullable = False)
    animal_id =db.Column(db.Integer, db.ForeignKey('animals.id'), nullable = False)
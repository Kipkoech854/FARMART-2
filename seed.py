from App import create_app, db
from App.models.Farmers import Farmer
from App.models.Users import User  
from App.extensions import bcrypt

app = create_app()

with app.app_context():
    
    db.drop_all()
    db.create_all()

    
    user1 = User(
        username="john_doe",
        email="john@example.com",
        password=bcrypt.generate_password_hash("password123").decode("utf-8")
    )

    user2 = User(
        username="jane_doe",
        email="jane@example.com",
        password=bcrypt.generate_password_hash("password456").decode("utf-8")
    )

   
    farmer1 = Farmer(
        username="farmer_mike",
        email="mike@farm.com",
        phone=123456789,
        password=bcrypt.generate_password_hash("mikepass").decode("utf-8"),
        profile_picture="https://example.com/mike.jpg"
    )

    farmer2 = Farmer(
        username="farmer_anne",
        email="anne@farm.com",
        phone=987654321,
        password=bcrypt.generate_password_hash("annepass").decode("utf-8"),
        profile_picture="https://example.com/anne.jpg"
    )

    db.session.add_all([user1, user2, farmer1, farmer2])
    db.session.commit()

    print("✅ Seeded test users and farmers.")

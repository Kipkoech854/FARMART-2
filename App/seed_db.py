from App import create_app, db
from App.models.Users import User
from App.models.Animals import Animal, Animalimages
from werkzeug.security import generate_password_hash

def seed_database():
    app = create_app('development')
    with app.app_context():
        # Create a test user
        hashed_password = generate_password_hash('testpass123', method='pbkdf2:sha256')
        test_user = User(
            id=1,
            username='testfarmer',
            email='test@example.com',
            password=hashed_password,
            role='farmer'
        )
        
        # Add the user to the database
        db.session.add(test_user)
        
        # Create some sample animals
        animals = [
            {
                'id': 1,
                'name': 'Daisy',
                'type': 'Cow',
                'breed': 'Holstein',
                'age': 3,
                'price': 1200.0,
                'description': 'Healthy dairy cow',
                'farmer_id': 1,
                'images': ['https://example.com/cow1.jpg']
            },
            {
                'id': 2,
                'name': 'Betsy',
                'type': 'Cow',
                'breed': 'Jersey',
                'age': 4,
                'price': 1500.0,
                'description': 'High milk production',
                'farmer_id': 1,
                'images': ['https://example.com/cow2.jpg']
            },
            {
                'id': 3,
                'name': 'Molly',
                'type': 'Goat',
                'breed': 'Nubian',
                'age': 2,
                'price': 800.0,
                'description': 'Friendly and good for milk',
                'farmer_id': 1,
                'images': ['https://example.com/goat1.jpg']
            }
        ]
        
        # Add animals to the database
        for animal_data in animals:
            animal = Animal(
                id=animal_data['id'],
                name=animal_data['name'],
                type=animal_data['type'],
                breed=animal_data['breed'],
                age=animal_data['age'],
                price=animal_data['price'],
                description=animal_data['description'],
                farmer_id=animal_data['farmer_id']
            )
            db.session.add(animal)
            
            # Add animal images
            for img_url in animal_data['images']:
                img = Animalimages(url=img_url, animal_id=animal.id)
                db.session.add(img)
        
        # Commit all changes
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database()

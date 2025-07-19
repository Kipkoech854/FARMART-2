from App import create_app, db
from App.models.Users import User
from App.models.Animals import Animal, Animalimages

def init_db():
    app = create_app('development')
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()

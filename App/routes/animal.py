from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from App.extensions import db
from App.models.Animals import Animal, Animalimages
from App.Schema.animal_schemas import AnimalSchema, AnimalimagesSchema

animals_blueprint = Blueprint('animals', __name__)

animal_schema = AnimalSchema()
animals_schema = AnimalSchema(many=True)

@animals_blueprint.route('/animals', methods=['POST'])
@jwt_required()
def create_animal():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    new_animal = Animal(
        name=data.get('name'),
        type=data.get('type'),
        breed=data.get('breed'),
        age=data.get('age'),
        price=data.get('price'),
        description=data.get('description'),
        farmer_id=current_user_id
    )
    
    db.session.add(new_animal)
    db.session.commit()
    
    if 'images' in data and data['images']:
        for image_url in data['images']:
            new_image = Animalimages(url=image_url, animal_id=new_animal.id)
            db.session.add(new_image)
        db.session.commit()
    
    return animal_schema.jsonify(new_animal), 201

@animals_blueprint.route('/animals', methods=['GET'])
def get_all_animals():
    # Get query parameters
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'asc')
    
    # Start with base query
    query = Animal.query.filter_by(is_available=True)
    
    # Apply search filter if provided
    if search:
        search = f"%{search}%"
        query = query.filter(
            (Animal.name.ilike(search)) |
            (Animal.breed.ilike(search)) |
            (Animal.type.ilike(search)) |
            (Animal.description.ilike(search))
        )
    
    # Apply sorting
    if hasattr(Animal, sort_by):
        sort_column = getattr(Animal, sort_by)
        if sort_order.lower() == 'desc':
            sort_column = sort_column.desc()
        query = query.order_by(sort_column)
    
    # Execute query
    animals = query.all()
    return jsonify(animals_schema.dump(animals)), 200

@animals_blueprint.route('/animals/<int:animal_id>', methods=['GET'])
def get_animal(animal_id):
    animal = Animal.query.get_or_404(animal_id)
    return animal_schema.jsonify(animal), 200

@animals_blueprint.route('/animals/<int:animal_id>', methods=['PUT'])
@jwt_required()
def update_animal(animal_id):
    animal = Animal.query.get_or_404(animal_id)
    current_user_id = get_jwt_identity()
    
    # Ensure both IDs are integers for comparison
    if int(animal.farmer_id) != int(current_user_id):
        return jsonify({"message": "Unauthorized"}), 403
    
    data = request.get_json()
    animal.name = data.get('name', animal.name)
    animal.type = data.get('type', animal.type)
    animal.breed = data.get('breed', animal.breed)
    animal.age = data.get('age', animal.age)
    animal.price = data.get('price', animal.price)
    animal.description = data.get('description', animal.description)
    animal.is_available = data.get('is_available', animal.is_available)
    
    if 'images' in data:
        Animalimages.query.filter_by(animal_id=animal_id).delete(synchronize_session=False)
        for image_url in data['images']:
            new_image = Animalimages(url=image_url, animal_id=animal_id)
            db.session.add(new_image)
    
    db.session.commit()
    return animal_schema.jsonify(animal), 200

@animals_blueprint.route('/animals/<int:animal_id>', methods=['DELETE'])
@jwt_required()
def delete_animal(animal_id):
    animal = Animal.query.get_or_404(animal_id)
    current_user_id = get_jwt_identity()
    
    # Ensure both IDs are integers for comparison
    if int(animal.farmer_id) != int(current_user_id):
        return jsonify({"message": "Unauthorized"}), 403
    
    db.session.delete(animal)
    db.session.commit()
    return jsonify({"message": "Animal deleted successfully"}), 200

@animals_blueprint.route('/farmers/animals', methods=['GET'])
@jwt_required()
def get_farmer_animals():
    current_user_id = get_jwt_identity()
    animals = Animal.query.filter_by(farmer_id=current_user_id).all()
    return jsonify(animals_schema.dump(animals)), 200
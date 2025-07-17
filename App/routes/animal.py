from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from App.extensions import db
from App.models.Animals import Animal, AnimalImage
from App.Schema.animal_schemas import AnimalSchema, AnimalImageSchema


animals_blueprint = Blueprint('animals', __name__)

animal_schema = AnimalSchema()
animals_schema = AnimalSchema(many=True)

@animals_blueprint.route('/animals', methods=['POST'])
@jwt_required()
def create_animal():
    print(">>> Entered create_animal route")
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON received or Content-Type not set to application/json"}), 400
    user_id =get_jwt_identity()
    current_user_id = user_id
    print("Current user ID:", current_user_id)

    try:
        new_animal = Animal(
            name=data.get('name'),
            type=data.get('type'),
            breed=data.get('breed'),
            age=data.get('age'),
            price=data.get('price'),
            description=data.get('description'),
            is_available=True,
            farmer_id=current_user_id
        )
        db.session.add(new_animal)
        db.session.commit()

        image_urls = data.get('images', [])
        for url in image_urls:
            new_image = AnimalImage(url=url, animal_id=new_animal.id)
            db.session.add(new_image)
        db.session.commit()

        animal_with_images = Animal.query.get(new_animal.id)

        return jsonify(animal_schema.dump(animal_with_images)), 201

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500



@animals_blueprint.route('/animals', methods=['GET'])
def get_all_animals():
    animals = Animal.query.filter_by(is_available=True).all()
    return jsonify(animals_schema.dump(animals)), 200

@animals_blueprint.route('/animals/<string:animal_id>', methods=['GET'])
def get_animal(animal_id):
    animal = Animal.query.get_or_404(animal_id)
    return animal_schema.jsonify(animal), 200

@animals_blueprint.route('/animals/<string:animal_id>', methods=['PUT'])
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

@animals_blueprint.route('/animals/<string:animal_id>', methods=['DELETE'])
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
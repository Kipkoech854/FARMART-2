from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from App.extensions import db
from App.models.Animals import Animal, AnimalImage
from App.Schema.animal_schemas import AnimalSchema, AnimalImageSchema
import requests
from App.models.Likes import Like
import os
from werkzeug.utils import secure_filename
from App.Utils.Animal_email_sender import send_animal_creation_confirmation
from sqlalchemy import and_


animals_blueprint = Blueprint('animals', __name__)

animal_schema = AnimalSchema()
animals_schema = AnimalSchema(many=True)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@animals_blueprint.route('/animals/create', methods=['POST'])
@jwt_required()
def create_animal():
    print(">>> Entered create_animal route")
    user_id = get_jwt_identity()
    print("Current user ID:", user_id)

    # Ensure the uploads folder exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    try:
        # Parse form fields
        name = request.form.get('name')
        type_ = request.form.get('type')
        breed = request.form.get('breed')
        age = request.form.get('age')
        price = request.form.get('price')
        location = request.form.get('location')
        description = request.form.get('description')
        is_available = request.form.get('is_available') == 'true'

        new_animal = Animal(
            name=name,
            type=type_,
            breed=breed,
            age=int(age),
            price=float(price),
            description=description,
            is_available=is_available,
            farmer_id=user_id,
            location=location
        )
        db.session.add(new_animal)
        db.session.commit()

        images = request.files.getlist('images')
        for file in images:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)

                file_url = f"/static/uploads/{filename}"  
                image = AnimalImage(url=file_url, animal_id=new_animal.id)
                db.session.add(image)

        db.session.commit()

        # Build payload and send email
        animal_with_images = Animal.query.get(new_animal.id)
        payload = animal_schema.dump(animal_with_images)
        payload['farmer_id'] = user_id
        send_animal_creation_confirmation(payload)

        return jsonify(payload), 201

    except Exception as e:
        print("Error:", str(e))
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


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



@animals_blueprint.route('/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    user_id = get_jwt_identity()
    try:
        from App.Utils.Recommendation import recommend_animals_for_user
        recommended = recommend_animals_for_user(user_id)
        return jsonify([AnimalSchema().dump(animal) for animal in recommended]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500




@animals_blueprint.route('/toggle/<string:animal_id>', methods=['POST'])
@jwt_required()
def toggle_like(animal_id):
    user_id = get_jwt_identity()

  
    existing_like = Like.query.filter_by(user_id=user_id, animal_id=animal_id).first()

    if existing_like:
       
        db.session.delete(existing_like)
        db.session.commit()
        return jsonify({'message': 'Unliked successfully'}), 200
    else:
       
        new_like = Like(
            id=str(uuid.uuid4()),
            user_id=user_id,
            animal_id=animal_id
        )
        db.session.add(new_like)
        db.session.commit()
        return jsonify({'message': 'Liked successfully'}), 201



@animals_blueprint.route('/search', methods=['GET'])
def search_animals():
    try:
        # Get query parameters with defaults
        animal_type = request.args.get('type')
        breed = request.args.get('breed')
        location = request.args.get('location')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        
        # Start with base query
        query = Animal.query.filter(Animal.is_available == True)
        
        # Build filters dynamically
        filters = []
        if animal_type:
            filters.append(Animal.type.ilike(f'%{animal_type}%'))
        if breed:
            filters.append(Animal.breed.ilike(f'%{breed}%'))
        if location:
            filters.append(Animal.location.ilike(f'%{location}%'))
        if min_price is not None:
            filters.append(Animal.price >= min_price)
        if max_price is not None:
            filters.append(Animal.price <= max_price)
        
        # Apply all filters
        if filters:
            query = query.filter(and_(*filters))
        
        # Execute query
        animals = query.all()
        
        # Format response with animal images
        results = []
        for animal in animals:
            animal_data = {
                'id': animal.id,
                'name': animal.name,
                'type': animal.type,
                'breed': animal.breed,
                'age': animal.age,
                'price': animal.price,
                'description': animal.description,
                'location': animal.location,
                'images': [img.url for img in animal.images]
            }
            results.append(animal_data)
        
        return jsonify({
            'success': True,
            'count': len(results),
            'animals': results
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500        
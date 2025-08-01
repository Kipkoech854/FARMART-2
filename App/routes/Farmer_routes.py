from flask import Blueprint, request, jsonify, url_for, redirect
from App.extensions import db
from App.models.Farmers import Farmer
from App.models.Animals import Animal
from App.models.Feedback import Feedback
from App.extensions import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from App.Utils.Token_Utils import generate_verification_token, confirm_verification_token
from App.Utils.Verification_mails import send_farmer_welcome_email, send_verification_email
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import cross_origin
from werkzeug.utils import secure_filename
import os
import uuid
from App.Schema.Farmer_schema import FarmersSchema
from itsdangerous import SignatureExpired, BadSignature
from App.Schema.Animal_schema import AnimalSchema




farmer_routes = Blueprint('farmer_routes', __name__)


@farmer_routes.route('/farmers/register', methods=['POST'])
def register_farmer():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    username = data.get('username')

    if not email or not password or not username:
        return jsonify({"error": "Missing required fields"}), 400

    # Prevent duplicate email registrations
    existing = Farmer.query.filter_by(email=email).first()
    if existing:
        return jsonify({"error": "Email already registered"}), 409

    # Hash password before encoding it
    hashed_password = generate_password_hash(password)

    # Prepare token payload
    token_data = {
        'email': email,
        'username': username,
        'password': hashed_password,
        'phone': data.get('phone'),
        'profile_picture': data.get('profile_picture')
    }

    token = generate_verification_token(token_data)
    verify_url = url_for('farmer_routes.verify_email', token=token, _external=True)
    send_verification_email(email, username, verify_url)

    return jsonify({
        "message": "Check your email to verify your account. Your data will only be saved after verification."
    }), 200


@farmer_routes.route('/farmers/login', methods=['POST'])
def login_farmer():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    farmer = Farmer.query.filter_by(email=email).first()
    if farmer and farmer.check_password(password):
        if farmer.verified != 'verified':
            return jsonify({"error": "Account not verified. Please check your email."}), 403

        # Add role here
        access_token = create_access_token(
            identity=farmer.id,
            additional_claims={
            "username": farmer.username,
            "email": farmer.email,
            "profile_picture": farmer.profile_picture,  
            "role": farmer.role
            }
            )


        return jsonify({
            "message": "Login successful",
            "token": access_token,
            "farmer": {
                "id": farmer.id,
                "username": farmer.username,
                "email": farmer.email,
                'profile_picture':farmer.profile_picture
            }
        }), 200

    return jsonify({"error": "Invalid credentials"}), 401



@farmer_routes.route('/farmers', methods=['PUT'])
@jwt_required()
def update_farmer():
    # Get current farmer from token
    id = get_jwt_identity()
    farmer = Farmer.query.get(id)
    if not farmer:
        return jsonify({"error": "Farmer not found"}), 404

    # Update text fields
    farmer.username = request.form.get('username', farmer.username)
    farmer.email = request.form.get('email', farmer.email)
    farmer.phone = request.form.get('phone', farmer.phone)

    # Handle image upload
    if 'profile_picture' in request.files:
        image = request.files['profile_picture']
        if image:
            upload_folder = os.path.join('App', 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)

            filename = secure_filename(f"{uuid.uuid4().hex}_{image.filename}")
            image_path = os.path.join(upload_folder, filename)
            image.save(image_path)

            # Save DB-friendly relative path
            farmer.profile_picture = f"static/uploads/{filename}"

    # Optional password update
    if request.form.get('password'):
        farmer.set_password(request.form.get('password'))

    db.session.commit()

    return jsonify({
        "message": "Farmer updated",
        "farmer": {
            "id": farmer.id,
            "username": farmer.username,
            "email": farmer.email,
            "phone": farmer.phone,
            "profile_picture": farmer.profile_picture
        }
    }), 200


@farmer_routes.route('/farmers', methods=['GET', 'OPTIONS'])  # <-- OPTIONS added
@jwt_required()
@cross_origin(origins="http://127.0.0.1:5173", supports_credentials=True)
def get_farmer():
    id = get_jwt_identity()
    farmer = Farmer.query.get(id)
    if not farmer:
        return jsonify({"error": "Farmer not found"}), 404

    return jsonify({
        "id": farmer.id,
        "username": farmer.username,
        "email": farmer.email,
        "phone": farmer.phone,
        "profile_picture": farmer.profile_picture
    })

@farmer_routes.route('/farmers', methods=['DELETE'])
@jwt_required()
def delete_farmer():
    id = get_jwt_identity()
    farmer = Farmer.query.get(id)
    if not farmer:
        return jsonify({"error": "Farmer not found"}), 404

    db.session.delete(farmer)
    db.session.commit()
    return jsonify({"message": "Farmer account deleted"})


@farmer_routes.route('/farmers/animals', methods=['GET'])
@jwt_required()
def get_farmer_animals():
    id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    pagination = Animal.query.filter_by(farmer_id=id).paginate(page=page, per_page=per_page, error_out=False)
    
    animals = [{
        "id": a.id,
        "name": a.name,
        "type": a.type,
        "breed": a.breed,
        "age": a.age,
        "price": a.price,
        "is_available": a.is_available
    } for a in pagination.items]

    return jsonify({
        "animals": animals,
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": pagination.page,
        "per_page": pagination.per_page
        })


@farmer_routes.route('/farmers/feedback', methods=['GET'])
@jwt_required()
def get_farmer_feedback():
    id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    pagination = Feedback.query.filter_by(farmer_id=id).paginate(page=page, per_page=per_page, error_out=False)
    
    feedbacks = [{
        "id": f.id,
        "user_id": f.user_id,
        "rating": f.rating,
        "comment": f.comment,
        "image_url": f.image_url
    } for f in pagination.items]
    
    return jsonify({
        "feedback": feedbacks,
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": pagination.page,
        "per_page": pagination.per_page})



@farmer_routes.route('/farmers/verify/<token>', methods=['GET'])
def verify_email(token):
    try:
        data = confirm_verification_token(token)
    except SignatureExpired:
        return redirect("https://your-frontend.com/verify?status=expired")
    except BadSignature:
        return redirect("https://your-frontend.com/verify?status=invalid")
    except Exception as e:
        return redirect(f"https://your-frontend.com/verify?status=error&msg={str(e)}")

    email = data.get('email')
    username = data.get('username')

    # Prevent duplicate creation
    if Farmer.query.filter_by(email=email).first():
        return redirect("https://your-frontend.com/verify?status=already_exists")

    new_farmer = Farmer(
        email=email,
        username=username,
        phone=data.get('phone'),
        profile_picture=data.get('profile_picture'),
        verified='verified',
        password_hash=data['password']  
        )

    

    db.session.add(new_farmer)
    db.session.commit()

    send_farmer_welcome_email(email, username)

    # Issue token now that farmer is registered
    access_token = create_access_token(
        identity=new_farmer.id,
        additional_claims={"role": "farmer"}
    )

    return redirect(f"https://moomall.netlify.app/verify?status=success&token={access_token}&email={email}")


@farmer_routes.route('/adminFarmers', methods=['GET'])
def get_all_farmers():
    farmers = Farmer.query.limit(100).all()  # Optional: limit results

    if not farmers:
        return jsonify({'error': 'there are no registered farmers yet'}), 404

    return jsonify(FarmersSchema(many=True, exclude=['animals']).dump(farmers)), 200


@farmer_routes.route('/adminFarmers/<string:farmer_id>/animals', methods=['GET'])
def get_each_farmer_animals(farmer_id):
    farmer = Farmer.query.get_or_404(farmer_id)
    return jsonify(AnimalSchema(many=True).dump(farmer.animals)), 200


@farmer_routes.route('/adminFarmers/search', methods=['GET'])
def search_farmers():
    query = request.args.get('query', '', type=str).strip()

    if not query:
        return jsonify({'error': 'Search query is required'}), 400

    farmers = Farmer.query.filter(
        db.or_(
            Farmer.username.ilike(f"%{query}%"),
            Farmer.email.ilike(f"%{query}%")
        )
    ).limit(50).all()

    if not farmers:
        return jsonify({'message': 'No matching farmers found'}), 404

    return jsonify(FarmersSchema(many=True, exclude=['animals']).dump(farmers)), 200

@farmer_routes.route('/farmers/<uuid:farmer_id>/toggle-verify', methods=['PUT'])
def toggle_verify(farmer_id):
    farmer = Farmer.query.get_or_404(farmer_id)
    farmer.verified = 'disabled' if farmer.verified == 'verified' else 'verified'
    db.session.commit()
    return jsonify(success=True)


from flask import Blueprint, request, jsonify, url_for, redirect
from App.extensions import db
from App.models.Farmers import Farmer
from App.models.Animals import Animal
from App.models.Feedback import Feedback
from App.extensions import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from App.Utils.Token_Utils import generate_verification_token, confirm_verification_token
from App.Utils.Verification_mails import send_verification_email



farmer_routes = Blueprint('farmer_routes', __name__)


@farmer_routes.route('/farmers/register', methods=['POST'])
def register_farmer():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    username = data.get('username')

    if not email or not password or not username:
        return jsonify({"error": "Missing required fields"}), 400

    existing = Farmer.query.filter_by(email=email).first()
    if existing:
        return jsonify({"error": "Email already registered"}), 409

    new_farmer = Farmer(
        email=email,
        username=username,
        phone=data.get('phone'),
        profile_picture=data.get('profile_picture'),
        verified='unverified'
    )
    new_farmer.set_password(password)

    db.session.add(new_farmer)
    db.session.commit()

  
    token = generate_verification_token(email)
    verify_url = url_for('farmer_routes.verify_email', token=token, _external=True)

  
    send_verification_email(email, username, verify_url)

    return jsonify({
        "message": "Farmer registered. Please verify your email.",
        "farmer": {
            "id": new_farmer.id,
            "username": new_farmer.username,
            "email": new_farmer.email
        }
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

        access_token = create_access_token(identity=farmer.id)
        return jsonify({
            "message": "Login successful",
            "token": access_token,
            "farmer": {
                "id": farmer.id,
                "username": farmer.username,
                "email": farmer.email
            }
        }), 200

    return jsonify({"error": "Invalid credentials"}), 401



@farmer_routes.route('/farmers', methods=['PUT'])
@jwt_required()
def update_farmer():
    id = get_jwt_identity()
    farmer = Farmer.query.get(id)
    if not farmer:
        return jsonify({"error": "Farmer not found"}), 404

    data = request.json
    farmer.username = data.get('username', farmer.username)
    farmer.email = data.get('email', farmer.email)
    farmer.phone = data.get('phone', farmer.phone)
    farmer.profile_picture = data.get('profile_picture', farmer.profile_picture)
    
   
    if data.get('password'):
        farmer.set_password(data.get('password'))

    db.session.commit()
    return jsonify({"message": "Farmer updated", "farmer": farmer.username})


@farmer_routes.route('/farmers', methods=['GET'])
@jwt_required()
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
        email = confirm_verification_token(token)  
    except SignatureExpired:
        return redirect("https://your-frontend.com/verify?status=expired")
    except BadSignature:
        return redirect("https://your-frontend.com/verify?status=invalid")
    except Exception as e:
        return redirect(f"https://your-frontend.com/verify?status=error&msg={str(e)}")

    farmer = Farmer.query.filter_by(email=email).first()
    if not farmer:
        return redirect("https://your-frontend.com/verify?status=not_found")

    farmer.verified = 'verified'
    db.session.commit()

    return redirect(f"https://your-frontend.com/verify?status=success&email={farmer.email}")

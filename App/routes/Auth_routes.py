from flask import Blueprint, request, jsonify
from App import db
from App.models.Users import User  # from App.models.User import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"msg": "Email already exists"}), 400

    role = data.get('role', 'customer')
    
    user = User(
        username = data['username'],
        email = data['email'],
        password_hash = generate_password_hash(data['password']),
        role = role,
        profile_picture = data.get('profile_picture', None)
    )

    if not user.username or not user.email or not user.password_hash:
        return jsonify({"msg": "Missing required fields"}), 400
    
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg": "User registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({"msg": "Invalid email or password"}), 401
    
    # if user.role == 'disabled':
    #     return jsonify({"msg": "User account is disabled"}), 403

    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    if user:
        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "profile_picture": user.profile_picture
        }), 200
from flask import Blueprint, request, jsonify, redirect, url_for, current_app
from App import db
from App.models.Users import User  
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from App.Utils.Token_Utils import generate_verification_token, confirm_verification_token
from App.Utils.Verification_mails import send_verification_email, send_welcome_email












auth_bp = Blueprint('auth', __name__)



@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"msg": "Email already exists"}), 400

    required_fields = ['username', 'email', 'password']
    if not all(data.get(field) for field in required_fields):
        return jsonify({"msg": "Missing required fields"}), 400

    hashed_password = generate_password_hash(data['password'])



    token_data = {
        "username": data['username'],
        "email": data['email'],
        "password": hashed_password,
        "role": data.get('role', 'customer'),
        "profile_picture": data.get('profile_picture'),
        "phone": data.get('phone')  # optional
    }

    token = generate_verification_token(token_data)
    verify_url = url_for('auth.verify_email', token=token, _external=True) 
    send_verification_email(data['email'], data['username'], verify_url)

    return jsonify({"msg": "Verification email sent. Please check your inbox."}), 200


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()


    user = User.query.filter_by(email=data['email']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({"msg": "Invalid email or password"}), 401

    if user.verified == 'unverified':
        return jsonify({"msg": "Please verify your email before logging in."}), 403

    if user.verified == 'disabled':
        return jsonify({"msg": "Your account has been disabled."}), 403







    access_token = create_access_token(
        identity=user.id,
        additional_claims={
            "role": user.role,
            "username": user.username,
            "email": user.email,
            "profile_picture": user.profile_picture
        }
    )

    return jsonify(access_token=access_token), 200






@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404
    
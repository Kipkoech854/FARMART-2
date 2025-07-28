from flask import Blueprint, request, jsonify, redirect, url_for
from App import db
from App.models.Users import User  
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from App.Schema.Users_schema import UserSchema
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from flask import current_app
from App.Utils.Token_Utils import generate_verification_token
from App.Utils.Verification_mails import send_verification_email, send_welcome_email
from werkzeug.security import generate_password_hash

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
        "profile_picture": data.get('profile_picture')
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

    # Construct token with extra claims
    access_token = create_access_token(
        identity=user.id,
        additional_claims={
            "role": "customer",
            "username": user.username,
            "email": user.email,
            "profile_picture": user.profile_picture  # adjust field name if different
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

    if user:
        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "profile_picture": user.profile_picture
        }), 200

from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

@auth_bp.route('/verify/<token>', methods=['GET'])
def verify_email(token):
    try:
        
        user_data = confirm_verification_token(token)
    except Exception:
        return redirect("https://yourfrontend.com/verification-failed")

    
    if User.query.filter_by(email=user_data['email']).first():
        return redirect("https://yourfrontend.com/already-verified")

    user = User(
        username=user_data['username'],
        email=user_data['email'],
        phone=user_data['phone'],
        role=user_data.get('role', 'customer'),
        profile_picture=user_data.get('profile_picture'),
        verified=True
    )
    user.password_hash = user_data['password']

    db.session.add(user)
    db.session.commit()

    send_welcome_email(user.email, user.username)

    access_token = create_access_token(identity=user.id, additional_claims={"role": user.role})
    return redirect(f"https://moomall.netlify.app/verify?status=success&token={access_token}&email={email}")


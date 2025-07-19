from flask import Blueprint, request, jsonify, redirect
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

auth_bp = Blueprint('auth', __name__)



@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"msg": "Email already exists"}), 400

    role = data.get('role', 'customer')

    user = User(
        username=data['username'],
        email=data['email'],
        phone=data['phone'],
        role=role,
        profile_picture=data.get('profile_picture', None),
        verified=False 
    )
    user.set_password(data['password'])

    if not user.username or not user.email or not user.password:
        return jsonify({"msg": "Missing required fields"}), 400

    db.session.add(user)
    db.session.commit()

    # --- Generate token and send verification email ---
    token = generate_verification_token(user.email)
    verify_url = f"http://127.0.0.1:5555/auth/verify/{token}"  
    send_verification_email(user.email, user.username, verify_url)

    return jsonify({"msg": "User registered. Please check your email to verify your account."}), 201


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

@auth_bp.route('/verify/<token>', methods=['GET'])
def verify_email(token):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=3600)
    except Exception:
        return redirect("https://yourfrontend.com/verification-failed")  

    user = User.query.filter_by(email=email).first()
    if not user:
        return redirect("https://yourfrontend.com/user-not-found")

    if user.verified:
        return redirect("https://yourfrontend.com/already-verified")

    user.verified = True
    db.session.commit()

    send_welcome_email(user.email, user.username)

    return redirect("https://yourfrontend.com/verified")
from flask import Blueprint, request, jsonify, redirect, url_for, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message

from App import db
from App.models.Users import User  
from App.Schema.Users_schema import UserSchema
from App.Utils.Token_Utils import generate_verification_token, confirm_verification_token
from App.Utils.Verification_mails import send_verification_email, send_welcome_email


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Check if email already exists
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({"msg": "Email already exists"}), 400

    # Check for required fields
    required_fields = ['username', 'email', 'password']
    if not all(data.get(field) for field in required_fields):
        return jsonify({"msg": "Missing required fields"}), 400

    # Store plain password temporarily for hashing during verification
    token_data = {
        "username": data['username'],
        "email": data['email'],
        "password": data['password'],  # plain password (will be hashed during verification)
        "role": data.get('role', 'customer'),
        "profile_picture": data.get('profile_picture'),
        "phone": data.get('phone')  # optional
    }

    # Generate verification token and send email
    token = generate_verification_token(token_data)
    verify_url = url_for('auth.verify_email', token=token, _external=True)
    send_verification_email(data['email'], data['username'], verify_url)

    return jsonify({"msg": "Verification email sent. Please check your inbox."}), 200





@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    user = User.query.filter_by(email=data.get('email')).first()

    if not user or not user.check_password(data.get('password')):
        return jsonify({"msg": "Invalid email or password"}), 401

    if user.verified == 'unverified':
        return jsonify({"msg": "Please verify your email before logging in."}), 403

    if user.verified == 'disabled':
        return jsonify({"msg": "Your account has been disabled."}), 403

    # Construct token with extra claims
    access_token = create_access_token(
        identity=user.id,
        additional_claims={
            "role": user.role,
            "username": user.username,
            "email": user.email,
            "profile_picture": user.profile_picture  # adjust field name if needed
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

    # Create user and hash password here
    user = User(
        username=user_data['username'],
        email=user_data['email'],
        phone=user_data.get('phone'),
        role=user_data.get('role', 'customer'),
        profile_picture=user_data.get('profile_picture'),
        verified=True
    )
    user.set_password(user_data['password'])  # hash it properly here

    db.session.add(user)
    db.session.commit()

    send_welcome_email(user.email, user.username)

    access_token = create_access_token(identity=user.id, additional_claims={"role": user.role})
    return redirect(f"https://moomall.netlify.app/verify?status=success&token={access_token}&email={user.email}")
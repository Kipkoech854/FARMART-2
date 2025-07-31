from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from App.models.Users import User
from App import db
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from functools import wraps
from werkzeug.utils import secure_filename
import os
from App.Schema.Users_schema import UserSchema
from flask import current_app



user_bp = Blueprint('user', __name__)

def role_required(*required_roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get('role') not in required_roles:
                return jsonify({"error": "Access denied"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper
@user_bp.route('/user', methods=['PATCH'])
@jwt_required()
def update_user():
    current_user_id = get_jwt_identity()
    username = request.form.get('username')
    email = request.form.get('email')
    profile_pic = request.files.get('profilePicture')

    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if get_jwt()["role"] != "customer":
        return jsonify({'error': 'Forbidden'}), 403

    if username:
        user.username = username
    if email:
        user.email = email

    if profile_pic:
        filename = secure_filename(profile_pic.filename)

        # ✅ Save inside static/uploads using absolute path
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)

        full_path = os.path.join(upload_folder, filename)
        profile_pic.save(full_path)

        # ✅ Save relative path (Flask will serve it via /static/)
        user.profile_picture = f"uploads/{filename}"
    db.session.commit()
    return jsonify(UserSchema().dump(user)), 200



@user_bp.route('/user', methods=['DELETE'])
@jwt_required()
 
def delete_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"msg": "User deleted successfully"}), 200

@user_bp.route('/user', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_user(user_id):
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200
    
@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    # Get current user's ID from JWT
    current_user_id = get_jwt_identity()
    
    # Query the database for this user
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
        "profile_picture": user.profile_picture,
        "verified": user.verified
    }), 200
    

@user_bp.route('/adminUsers', methods=['GET'])
def get_all_users():
    users = User.query.all()

    if not users:
        return jsonify({'error': 'You have no registered users'}), 404

    return jsonify(UserSchema(many=True).dump(users)), 200

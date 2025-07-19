from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from App.models.Users import User
from App import db
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from functools import wraps


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
@role_required('admin')
def update_user(user_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    if 'role' in data:
        user.role = data['role']
    if 'profile_picture' in data:
        user.profile_picture = data['profile_picture']

    db.session.commit()
    return jsonify({"msg": "User updated successfully"}), 200

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

    

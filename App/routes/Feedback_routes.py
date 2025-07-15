from flask import Blueprint, request, jsonify
from App import db
from models.Feedback import Feedback
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from functools import wraps

feedback_bp = Blueprint('feedback', __name__)

def role_required(*required_role):

    def wrapper(fn):

        @wraps(fn)

        def decorator(*args, **kwargs):

            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get('role') != required_role:
                return jsonify({"error": "Access denied"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper


@feedback_bp.route('/feedback', methods=['POST'])
@jwt_required()
@role_required('user')
def submit_feedback():
    data = request.get_json()
    user_id = get_jwt_identity()

    feedback = Feedback(message=data['message'], user_id=user_id)
    db.session.add(feedback)
    db.session.commit()

    return jsonify({"message": "Feedback submitted"}), 201
from flask import Blueprint, jsonify, request
from App.models.Farmers import Farmer  
from App.extensions import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from App.models.Animals import Animal, AnimalImage
import requests
from App.models.Users import User
from App.Schema.Users_schema import UserSchema
from App.Utils.mail_utils import get_farmer_contact

Mailservice_bp = Blueprint('Mailservice_bp', __name__)

@Mailservice_bp.route('/farmers/<string:farmer_id>', methods=['GET'])
def get_farmer_email_username(farmer_id):
    farmer = Farmer.query.get(farmer_id)
    if not farmer:
        return jsonify({"error": "Farmer not found"}), 404

    return jsonify({
        "email": farmer.email,
        "username": farmer.username
    }), 200


@Mailservice_bp.route('/mail/farmer-item-details', methods=['POST'])
def group_items_by_farmer():
    try:
        data = request.get_json()
        if not data or "items" not in data:
            return jsonify({"error": "Invalid request. 'items' key missing"}), 400

        items = data["items"]
        result = group_items_by_farmer_util(items)
        return jsonify(result), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print("Server error:", str(e))
        return jsonify({"error": "Internal server error"}), 500

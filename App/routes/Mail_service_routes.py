from flask import Blueprint, jsonify
from App.models.Farmers import Farmer  
from App.extensions import db

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
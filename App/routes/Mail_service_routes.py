from flask import Blueprint, jsonify, request
from App.models.Farmers import Farmer  
from App.extensions import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from App.models.Animals import Animal, AnimalImage
import requests
from App.models.Users import User
from App.Schema.Users_schema import UserSchema

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



@Mailservice_bp.route('/Users/<string:user_id>', methods = ['GET'])
def get_user_email_username(user_id):
    id  = user_id
    user = User.query.get(id)
    if not user:
        return jsonify([{'error': 'User not found'}]), 404

    return  jsonify(UserSchema().dump(user)), 200


@Mailservice_bp.route('/mail/farmer-item-details', methods=['POST'])
def group_items_by_farmer():
    try:
        data = request.get_json()
        if not data or "items" not in data:
            return jsonify({"error": "Invalid request. 'items' key missing"}), 400

        items = data["items"]
        if not isinstance(items, list):
            return jsonify({"error": "'items' must be a list"}), 400

        farmer_items = {}

        for item in items:
            animal_id = item.get("animal_id")
            if not animal_id:
                continue

            animal = Animal.query.get(animal_id)
            if not animal:
                continue

            farmer_id = animal.farmer_id
            if farmer_id not in farmer_items:
                farmer_items[farmer_id] = []

            enriched_item = {
                "animal_id": animal.id,
                "name": animal.name,
                "type": animal.type,
                "breed": animal.breed,
                "age": animal.age,
                "price": animal.price,
                "description": animal.description,
                "is_available": animal.is_available,
                "image_count": len(animal.images),
                "quantity": item.get("quantity"),
                "price_at_order_time": item.get("price_at_order_time")
            }

            farmer_items[farmer_id].append(enriched_item)

        response_payload = []

        for farmer_id, items_list in farmer_items.items():
            try:
                res = requests.get(f"http://127.0.0.1:5555/api/Mailservice/farmers/{farmer_id}")
                if res.status_code == 200:
                    farmer_data = res.json()
                    response_payload.append({
                        "id": farmer_id,
                        "email": farmer_data.get("email"),
                        "username": farmer_data.get("username"),
                        "items": items_list
                    })
                else:
                    print(f"Farmer not found: {farmer_id}")
            except Exception as e:
                print(f"Error fetching farmer {farmer_id}:", str(e))
                return jsonify({"error": f"Failed to fetch farmer info for {farmer_id}"}), 500

        return jsonify(response_payload), 200

    except Exception as e:
        print("Server error:", str(e))
        return jsonify({"error": "Internal server error"}), 500

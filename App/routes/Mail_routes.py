from flask import Blueprint,jsonify,request
from flask_mail import Message
from App.extensions import mail
import requests
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_mail import Message
from App.Utils.mail_utils import get_farmer_contact, get_user_contact, group_items_by_farmer_util

Mail_bp = Blueprint('Mail_bp', __name__)

@Mail_bp.route("/createAnimalconformation", methods=["POST"])
def animal_creation_confirmation_route():
    data = request.get_json()
    id = data['id']
    name = data['name']
    breed = data['breed']
    age = data['age']
    price = data['price']
    description = data['description']
    images = data['images']
    number = len(images)
    plural = 's' if number != 1 else ''
    farmer_id = data['farmer_id']

    try:
        
        farmer_data = get_farmer_contact(farmer_id)
        username = farmer_data['username']
        receipient = farmer_data['email']
        print(f"{receipient}")
        print(f"{username}")

    except Exception as e:
        print("farmer_response failed:", e)
        return jsonify({"error": "Farmer request failed"}), 500

    try:
        msg = Message(
            'FARMART',
            sender='farmart597@gmail.com',
            recipients=[receipient]
        )
        msg.body = f"""
Hello {username},

Your new product has been successfully created with the following details:

Product ID: {id}
Name: {name}
Breed: {breed}
Age: {age} years
Price: KES {price}
Description: {description}

You have uploaded {number} image{plural} for this product.

Thank you for using our platform!

Best regards,  
The FarmArt Team
        """
        print(">> Sending email now...")
        mail.send(msg)
        print(">> Email sent!")
        return jsonify({'message': 'Email sent successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@Mail_bp.route('/test-email', methods=['POST'])
def test_email():
    try:
        msg = Message(
            subject='Test Email from FarmArt',
            sender = 'farmart597@gmail.com',
            recipients=['gideonkipkoech854@gmail.com'],  # Replace with your test email
            body='This is a test message to verify the email system is working.'
        )
        mail.send(msg)
        return jsonify({'message': 'Test email sent successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

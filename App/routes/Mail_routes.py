from flask import Blueprint,jsonify,request
from flask_mail import Message
from App.extensions import mail
import requests


Mail_bp = Blueprint('Mail_bp', __name__)

@Mail_bp.route('/Order-User/<string:userid>', methods=['POST'])
def Send_order_confirmation_user(userid):
    data = request.get_json()
    id = data['id']
    created_at = data['created_at']
    amount = data['amount']
    items = data['items']
    number =len(items)
   
    try:
        msg = Message(
            'FARMART',
            sender='arvinkipo@gmail.com',
            recipients=[f"gideonkipkoech854@gmail.com"]
        )

        msg.body = (
            f"This is to confirm your order {id} which totalled {amount}. "
            f"The order was made at {created_at} and contains {number} items.An has been sent to the farmer for confirmation. "
            f"You will receive an email for confirmation in order to continue with Payment and delivery. "
            f"HAPPY SHOPPING!"
        )
        print("Sending to:", msg.recipients)
        print("Subject:", msg.subject)
        print("Body:", msg.body)

        mail.send(msg)
        return jsonify({'message': 'Email sent successfully'}), 200

    except Exception as e:
        return jsonify([{'error': str(e)}]), 500



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
        farmer_response = requests.get(
            f'http://127.0.0.1:5555/api/Mailservice/farmers/{farmer_id}'
        )
        if farmer_response.status_code != 200:
            print("Failed to get farmer details:", farmer_response.text)
            return jsonify({"error": "Farmer not found"}), 404

        farmer_data = farmer_response.json()
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
            sender='arvinkipo@gmail.com',
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
            sender = 'arvinkipo@gmail.com',
            recipients=['gideonkipkoech854@gmail.com'],  # Replace with your test email
            body='This is a test message to verify the email system is working.'
        )
        mail.send(msg)
        return jsonify({'message': 'Test email sent successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

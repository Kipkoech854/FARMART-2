from flask import Blueprint,jsonify,request
from flask_mail import Message
from App.extensions import mail
import requests
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity


Mail_bp = Blueprint('Mail_bp', __name__)

from flask import Blueprint, jsonify, request
import requests
from flask_mail import Message
from App.extensions import mail

Mail_bp = Blueprint('Mail_bp', __name__)

@Mail_bp.route('/Order-User/<string:user_id>', methods=['POST'])
def Send_order_confirmation_user(user_id):
    data = request.get_json()
    id = data.get('id')
    created_at = data.get('created_at')
    amount = data.get('amount')
    items = data.get('items', [])
    number = len(items)

    try:
        response = requests.get(f'http://127.0.0.1:5555/api/Mailservice/Users/{user_id}')
        if response.status_code != 200:
            return jsonify({'error': f"Recipient mailservice error: {response.text}"}), 404

        recipient = response.json()
        email = recipient.get('email')
        username = recipient.get('username')

        msg = Message(
            subject='FARMART - Order Confirmation',
            sender='arvinkipo@gmail.com',
            recipients=[email] 
        )

        msg.body = (
            f"Hello {username},\n\n"
            f"This is to confirm your order **{id}**, which totaled KES {amount}. "
            f"The order was made at {created_at} and contains {number} item(s).\n\n"
            f"An email has been sent to the farmer for confirmation. "
            f"You will receive a follow-up email once the farmer confirms, so you can proceed with payment and delivery.\n\n"
            f"HAPPY SHOPPING!\nFARMART TEAM"
        )

        print("Preparing to send email...")
        mail.send(msg)
        print("Email sent successfully")
        return jsonify({'message': 'Email sent successfully'}), 200

    except Exception as e:
        print("Email sending failed:", str(e))
        return jsonify({'error': str(e)}), 500



@Mail_bp.route('/Order-farmer', methods=['POST'])
def Send_order_confirmation_farmer():
    data = request.get_json()
    
    if not data:
        return jsonify([{'error': 'Invalid or no data to send to farmers'}]), 400

    try:
        response = requests.post(
            'http://127.0.0.1:5555/api/Mailservice/mail/farmer-item-details',
            json=data
        )
        
        if response.status_code != 200:
            print('Failed to get farmer details:', response.text)
            return jsonify([{'error': 'Farmer details not found!'}]), 404

        farmers = response.json()

        for farmer in farmers:
            try:
                recipient_email = farmer.get('email')
                username = farmer.get('username')
                items = farmer.get('items', [])

                if not recipient_email or not items:
                    continue 

                
                order_lines = ""
                for item in items:
                    order_lines += f"""
----------------------------
Animal Name: {item.get('name')}
Type: {item.get('type')}
Breed: {item.get('breed')}
Age: {item.get('age')}
Available: {"Yes" if item.get('is_available') else "No"}
Price at Order Time: KES {item.get('price_at_order_time')}
Quantity Ordered: {item.get('quantity')}
Description: {item.get('description')}
Number of Images Listed: {item.get('image_count')}
"""

                msg = Message(
                    subject='FARMART - New Animal Order Received',
                    sender='arvinkipo@gmail.com',
                    recipients=[recipient_email]
                )

                msg.body = f"""
Hello {username},

You have received a new order for your listed animals on FARMART. Below are the details of the order:

{order_lines}

Please ensure the animal(s) are ready for delivery or pickup as per our platform’s fulfillment process. You can view or manage this order in your FarmArt dashboard.

If you have any questions or need assistance, feel free to reach out to our support team.

Thank you for using FarmArt!
Let’s keep farming digital. 🌱
"""

                print("Sending email to:", recipient_email)
                mail.send(msg)
                print("Email sent successfully to:", recipient_email)

            except Exception as e:
                print("Failed to send email to:", recipient_email)
                return jsonify([{'error': str(e)}]), 500

        return jsonify({'message': 'Emails sent successfully to all farmers'}), 200

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

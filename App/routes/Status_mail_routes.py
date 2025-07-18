from flask import Blueprint, jsonify, request
from App.models.Farmers import Farmer  
from App.extensions import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from App.models.Animals import Animal, AnimalImage
import requests
from App.models.Users import User
from App.Schema.Users_schema import UserSchema
from flask_mail import Message
from App.extensions import mail

Status_mail_bp = Blueprint('Status_mail_bp', __name__)

@Status_mail_bp.route('/Status-Changed-User', methods=['POST'])
def Send_order_status_change_user():
    data = request.get_json()
    id = data['user_id']

    if not data:
        return jsonify({'error': 'Invalid or no data to send to farmers'}), 400

    status = data.get('status', '').lower()

    # Conditional message
    if status == 'confirmed':
        line = (
            f"Please go over to our website and complete payment. "
            f"Make sure to input your shipping details. "
            f"The farmer will inform you on the day of delivery."
        )
    elif status == 'rejected':
        line = (
            f"We regret to inform you that the order could not go through. "
            f"Consider looking up other animals on our website and try again."
        )
    else:
        line = ""

    try:
        user_id = data['user_id']


        # Get user details
        user_response = requests.get(
            f"http://127.0.0.1:5555/api/Mailservice/Users/{user_id}"
        )

        if user_response.status_code != 200:
            print('Failed to get user details:', user_response.text)
            return jsonify({'error': 'Failed to retrieve user information'}), 400

        user_data = user_response.json()
        recipient_email = user_data.get('email')
        username = user_data.get('username')

        # Get farmer and item details
        response = requests.post(
            'http://127.0.0.1:5555/api/Mailservice/mail/farmer-item-details',
            json=data
        )

        if response.status_code != 200:
            print('Failed to get farmer details:', response.text)
            return jsonify({'error': 'Failed to retrieve farmer details'}), 404

        farmers = response.json()

        failed_emails = []
        successful_emails = []

        for farmer in farmers:
            items = farmer.get('items', [])

            if not recipient_email or not items:
                print(f"Skipping user with missing email or items: {user_data}")
                continue

            # Build the message body
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
                subject='FARMART - New Order Status Received',
                sender='arvinkipo@gmail.com',
                recipients=[recipient_email]
            )

            msg.body = f"""
Hello {username},

There is a new status update on your order. The farmer has *{status.upper()}* your order with the following details:

{order_lines}

{line}

If you have any questions or need assistance, feel free to reach out to our support team.

Thank you for using FarmArt!
Let’s keep farming digital. 🌱
"""

            try:
                mail.send(msg)
                successful_emails.append(recipient_email)
                print(f"Email sent successfully to {recipient_email}")
            except Exception as e:
                error_msg = str(e)
                print(f"Error sending email to {recipient_email}: {error_msg}")
                failed_emails.append({'email': recipient_email, 'error': error_msg})

        return jsonify({
            'message': 'Email dispatch complete',
            'successful': successful_emails,
            'failed': failed_emails
        }), 207 if failed_emails else 200

    except Exception as e:
        print("Critical failure:", str(e))
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@Status_mail_bp.route('/Status-Changed-Farmer', methods=['POST'])
def Send_status_change_update_farmer():
    data = request.get_json()
    status = data['status']
    

    if status == 'confirmed':
        line = (
            f'be on the lookout for information from the user on payment and shipping details.'
            f"make sure the shipping dates are within the stated days on our policy"
        )
    elif status == 'rejected':
        line = (
            f'Be on the lookout for more orders!'
        )
    else:
        line = ''

    if not data:
        return jsonify({'error': 'Invalid or no data to send to farmers'}), 400

    try:
        # Step 1: Get farmer item details
        response = requests.post(
            'http://127.0.0.1:5555/api/Mailservice/mail/farmer-item-details',
            json=data
        )
        
        if response.status_code != 200:
            print('Failed to get farmer details:', response.text)
            return jsonify({'error': 'Failed to retrieve farmer details'}), 404

        farmers = response.json()

        failed_emails = []
        successful_emails = []

        for farmer in farmers:
            recipient_email = farmer.get('email')
            username = farmer.get('username')
            items = farmer.get('items', [])

            if not recipient_email or not items:
                print(f"Skipping farmer with missing email or items: {farmer}")
                continue

            # Build the message body
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

            # Compose the email
            msg = Message(
                subject='FARMART - New Animal Order Received',
                sender='arvinkipo@gmail.com',
                recipients=[recipient_email]
            )

            msg.body = f"""
Hello {username},

This is to confirmed that you have {status}:

{order_lines}

{line}

If you have any questions or need assistance, feel free to reach out to our support team.

Thank you for using FarmArt!
Let’s keep farming digital. 🌱
"""

            try:
                mail.send(msg)
                successful_emails.append(recipient_email)
                print(f"Email sent successfully to {recipient_email}")
            except Exception as e:
                error_msg = str(e)
                print(f"Error sending email to {recipient_email}: {error_msg}")
                failed_emails.append({'email': recipient_email, 'error': error_msg})

        return jsonify({
            'message': 'Email dispatch complete',
            'successful': successful_emails,
            'failed': failed_emails
        }), 207 if failed_emails else 200

    except Exception as e:
        print("Critical failure:", str(e))
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


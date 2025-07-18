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

Delivery_mail_bp = Blueprint('Delivery_mail_bp', __name__)

@Delivery_mail_bp.route('/DeliveryMail-User', methods=['POST'])
def send_delivery_mail_user():
    print('Process started')
    data = request.get_json()
    user_id = data.get('user_id')
 
    if not data:
        return jsonify({'error': 'Invalid or no data to send to farmers'}), 400

    try:
      
        user_response = requests.get(f"http://127.0.0.1:5555/api/Mailservice/Users/{user_id}")
        if user_response.status_code != 200:
            print('Failed to get user details:', user_response.text)
            return jsonify({'error': 'Failed to retrieve user information'}), 400

        user_data = user_response.json()
        recipient_email = user_data.get('email')
        username = user_data.get('username')
        print(f"{recipient_email}")

       
        response = requests.post(
            'http://127.0.0.1:5555/api/Mailservice/mail/farmer-item-details',
            json=data
        )
        if response.status_code != 200:
            print('Failed to get farmer details:', response.text)
            return jsonify({'error': 'Failed to retrieve farmer details'}), 404

        farmers = response.json()

        
        all_items = []
        for farmer in farmers:
            items = farmer.get('items', [])
            if items:
                all_items.extend(items)

        if not recipient_email or not all_items:
            print("No valid recipient or items to send.")
            return jsonify({'error': 'No valid recipient or items to send.'}), 400

        
        order_lines = ""
        for item in all_items:
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
            subject='FARMART - Delivery confirmation',
            sender='arvinkipo@gmail.com',
            recipients=[recipient_email]
        )
        msg.body = f"""
Hello {username},

This email is a confirmation that you received delivery of the following items:

{order_lines}

If you have any questions or need assistance, feel free to reach out to our support team.

Thank you for using FarmArt!
Let’s keep farming digital. 🌱
"""
        mail.send(msg)

    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Delivery email sent successfully'}), 200




@Delivery_mail_bp.route('/DeliveryMail-Farmer', methods=['POST'])
def send_delivery_mail_farmer():
    print('Farmer delivery confirmation callback started')
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Invalid or no order data'}), 400

    try:
     
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
            email = farmer.get('email')
            name = farmer.get('username') or "Farmer"
            items = farmer.get('items', [])

            if not email or not items:
                print(f"Skipping farmer with missing data: {farmer}")
                continue

            order_lines = ""
            for item in items:
                order_lines += f"""
----------------------------
Animal Name: {item.get('name')}
Type: {item.get('type')}
Breed: {item.get('breed')}
Age: {item.get('age')}
Delivered: Yes ✅
Price at Order Time: KES {item.get('price_at_order_time')}
Quantity Ordered: {item.get('quantity')}
Description: {item.get('description')}
Number of Images Listed: {item.get('image_count')}
"""

            msg = Message(
                subject='FARMART - Order delivery confirmed by customer',
                sender='arvinkipo@gmail.com',
                recipients=[email]
            )

            msg.body = f"""
Hello {name},

Your customer has confirmed receipt of the following animal items:

{order_lines}

Thank you for fulfilling the order on FarmArt. 🌾
Keep growing!

- The FarmArt Team
"""

            try:
                mail.send(msg)
                successful_emails.append(email)
            except Exception as e:
                print(f"Failed to send email to {email}: {e}")
                failed_emails.append(email)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({
        'message': 'Emails sent to farmers.',
        'success_count': len(successful_emails),
        'failed_count': len(failed_emails),
        'failed_emails': failed_emails
    }), 200






@Delivery_mail_bp.route('/PaymentConfirmation-Farmer', methods=['POST'])
def send_payment_confirmation_farmer():
    print('Farmer payment confirmation callback started')
    data = request.get_json()
    payment_method = data.get('paymrnt_method', '').lower()

    # Conditional message
    if payment_method == 'card':
        line = (
            f"please visit your bank account and check the transaction"
        )
    elif payment_method == 'cash':
        line = (
            f"This has come from you assertaining you have received the cash "
        )
    else:
        line = ""

    if not data:
        return jsonify({'error': 'Invalid or no order data'}), 400

    try:
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
            email = farmer.get('email')
            name = farmer.get('username') or "Farmer"
            items = farmer.get('items', [])

            if not email or not items:
                print(f"Skipping farmer with missing data: {farmer}")
                continue

            order_lines = ""
            for item in items:
                order_lines += f"""
----------------------------
Animal Name: {item.get('name')}
Type: {item.get('type')}
Breed: {item.get('breed')}
Age: {item.get('age')}
Payment Received: Yes 💰
Price at Order Time: KES {item.get('price_at_order_time')}
Quantity Ordered: {item.get('quantity')}
Description: {item.get('description')}
Number of Images Listed: {item.get('image_count')}
"""

            msg = Message(
                subject='FARMART - Payment Received for Your Order',
                sender='arvinkipo@gmail.com',
                recipients=[email]
            )

            msg.body = f"""
Hello {name},

This is a confirmation that you have received payment for the following animals:

{line}

{order_lines}

Thank you for using FarmArt and continuing to support digital farming. 🚜

- The FarmArt Team
"""

            try:
                mail.send(msg)
                successful_emails.append(email)
            except Exception as e:
                print(f"Failed to send email to {email}: {e}")
                failed_emails.append(email)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({
        'message': 'Payment confirmation emails sent to farmers.',
        'success_count': len(successful_emails),
        'failed_count': len(failed_emails),
        'failed_emails': failed_emails
    }), 200




@Delivery_mail_bp.route('/PaymentConfirmation-User', methods=['POST'])
def send_payment_confirmation_user():
    print('Payment confirmation process started')
    data = request.get_json()
    
    user_id = data.get('user_id')
    order_id = data.get('id')
    amount_paid = data.get('amount')
    items = data.get('items', [])
    
    if not data or not user_id or not order_id or not items:
        return jsonify({'error': 'Missing required data'}), 400

    try:
       
        user_response = requests.get(f"http://127.0.0.1:5555/api/Mailservice/Users/{user_id}")
        if user_response.status_code != 200:
            print('Failed to get user details:', user_response.text)
            return jsonify({'error': 'Failed to retrieve user information'}), 400

        user_data = user_response.json()
        recipient_email = user_data.get('email')
        username = user_data.get('username')
        print(f"Sending payment email to {recipient_email}")

       
        item_lines = ""
        for item in items:
            item_lines += f"""
----------------------------
Animal ID: {item.get('animal_id')}
Quantity: {item.get('quantity')}
Price at Order Time: KES {item.get('price_at_order_time')}
"""

       
        msg = Message(
            subject='FARMART - Payment Confirmation',
            sender='arvinkipo@gmail.com',
            recipients=[recipient_email]
        )
        msg.body = f"""
Hello {username},

We have received your payment for Order ID: {order_id}.

Payment Details:
Amount Paid: KES {amount_paid}
Status: {'Paid' if data.get('paid') else 'Unpaid'}
Delivery Status: {'Delivered' if data.get('delivered') else 'Pending'}

Items in this order:
{item_lines}

Thank you for shopping with FarmArt!
Let’s keep farming digital. 🌱
"""
        mail.send(msg)

    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Payment confirmation email sent successfully'}), 200

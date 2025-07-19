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
from App.Utils.mail_utils import get_user_contact, group_items_by_farmer_util

Delivery_mail_bp = Blueprint('Delivery_mail_bp', __name__)


@Delivery_mail_bp.route('/PaymentConfirmation-Farmer', methods=['POST'])
def send_payment_confirmation_farmer():
    print('Farmer payment confirmation callback started')
    data = request.get_json()
    payment_method = data.get('paymrnt_method', '').lower()
    items = data['items']
    
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
        from App.Utils.mail_utils import group_items_by_farmer_util

        farmers = group_items_by_farmer_util(items)

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
                sender='farmart597@gmail.com',
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
        from App.Utils.mail_utils import get_user_contact

        user_data = get_user_contact(user_id)
        recipient_email = user_data['email']
        username = user_data['username']
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
            sender='farmart597@gmail.com',
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

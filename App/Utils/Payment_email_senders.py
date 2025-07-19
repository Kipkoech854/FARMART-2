from flask_mail import Message
from App.extensions import mail
from App.Utils.mail_utils import get_user_contact

def send_payment_confirmation_to_user(user_id, order_data):
    try:
        user_data = get_user_contact(user_id)
        recipient_email = user_data['email']
        username = user_data['username']

        items = order_data.get("items", [])
        item_lines = "\n".join([
            f"""
----------------------------
Animal ID: {item.get('animal_id')}
Quantity: {item.get('quantity')}
Price at Order Time: KES {item.get('price_at_order_time')}
""" for item in items
        ])

        msg = Message(
            subject='FARMART - Payment Confirmation',
            sender='farmart597@gmail.com',
            recipients=[recipient_email]
        )

        msg.body = f"""
Hello {username},

We have received your payment for Order ID: {order_data.get('id')}.

Payment Details:
Amount Paid: KES {order_data.get('amount')}
Status: {'Paid' if order_data.get('paid') else 'Unpaid'}
Delivery Status: {'Delivered' if order_data.get('delivered') else 'Pending'}

Items in this order:
{item_lines}

Thank you for shopping with FarmArt!
Let’s keep farming digital. 🌱
"""

        mail.send(msg)
        return True

    except Exception as e:
        print(f"Failed to send user payment email: {e}")
        return False




from flask_mail import Message
from App.extensions import mail
from App.Utils.mail_utils import group_items_by_farmer_util

def send_payment_confirmation_to_farmers(items, payment_method):
    try:
        line = {
            "card": "Please check your bank account for confirmation.",
            "cash": "This confirms you have received cash from the buyer."
        }.get(payment_method.lower(), "")

        farmers = group_items_by_farmer_util(items)

        failed_emails = []

        for farmer in farmers:
            email = farmer.get('email')
            name = farmer.get('username') or "Farmer"
            items = farmer.get('items', [])

            if not email or not items:
                print(f"Skipping farmer with missing data: {farmer}")
                continue

            item_lines = "\n".join([
                f"""
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
""" for item in items
            ])

            msg = Message(
                subject='FARMART - Payment Received for Your Order',
                sender='farmart597@gmail.com',
                recipients=[email]
            )

            msg.body = f"""
Hello {name},

This is a confirmation that you have received payment for the following animals:

{line}

{item_lines}

Thank you for using FarmArt and continuing to support digital farming. 🚜

- The FarmArt Team
"""

            try:
                mail.send(msg)
            except Exception as e:
                print(f"Failed to send email to {email}: {e}")
                failed_emails.append(email)

        return failed_emails  # empty list if all succeeded

    except Exception as e:
        print(f"Error sending farmer confirmations: {e}")
        return ['internal_error']

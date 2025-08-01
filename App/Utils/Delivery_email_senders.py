from App.Utils.mail_utils import get_user_contact, group_items_by_farmer_util
from flask_mail import Message
from App.extensions import mail

def send_delivery_email_to_user(user_id, items):
    try:
        user_data = get_user_contact(user_id)
        recipient_email = user_data['email']
        username = user_data['username']

        all_items = []
        for farmer in group_items_by_farmer_util(items):
            all_items.extend(farmer.get('items', []))

        if not recipient_email or not all_items:
            print("Missing recipient or items")
            return False

        order_lines = ""
        for item in all_items:
            order_lines += f"""----------------------------
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
            sender='farmart597@gmail.com',
            recipients=[recipient_email]
        )
        msg.body = f"""Hello {username},

This email is a confirmation that you received delivery of the following items:

{order_lines}

Thank you for using FarmArt!
Let’s keep farming digital. 🌱
"""
        mail.send(msg)
        return True

    except Exception as e:
        print(f"[User Email Error] {e}")  # <-- IMPORTANT
        return False




def send_delivery_email_to_farmers(items):
    farmers = group_items_by_farmer_util(items)
    failed = []

    for farmer in farmers:
        email = farmer.get('email')
        name = farmer.get('username', 'Farmer')
        farmer_items = farmer.get('items', [])

        if not email or not farmer_items:
            continue

        order_lines = ""
        for item in farmer_items:
            order_lines += f"""----------------------------
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
            sender='farmart597@gmail.com',
            recipients=[email]
        )
        msg.body = f"""Hello {name},

Your customer has confirmed receipt of the following animal items:

{order_lines}

Thank you for fulfilling the order on FarmArt. 🌾
Keep growing!
- The FarmArt Team
"""
        try:
            mail.send(msg)
        except Exception as e:
            print(f"[Farmer Email Failed] {email} — {e}")
            failed.append(email)

    return failed

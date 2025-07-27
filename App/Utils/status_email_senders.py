from flask_mail import Message
from App.extensions import mail
from App.models.Users import User
from App.Utils.mail_utils import group_items_by_farmer_util

def format_order_lines(items):
    lines = ""
    for item in items:
        lines += (
            f"\n----------------------------\n"
            f"Animal Name       : {item.get('name')}\n"
            f"Type              : {item.get('type')}\n"
            f"Breed             : {item.get('breed')}\n"
            f"Age               : {item.get('age')}\n"
            f"Available         : {'Yes' if item.get('is_available') else 'No'}\n"
            f"Price at Order    : KES {item.get('price_at_order_time')}\n"
            f"Quantity Ordered  : {item.get('quantity')}\n"
            f"Description       : {item.get('description')}\n"
            f"Images Provided   : {item.get('image_count')}\n"
        )
    return lines

def send_status_update_to_user(data):
    try:
        user_id = data.get('user_id')
        status = data.get('status', '').lower()
        items = data.get('items', [])

        if not user_id or not status or not items:
            return False, "Missing user_id, status, or items."

        user = User.query.get(user_id)
        if not user:
            return False, "User not found."

        farmers = group_items_by_farmer_util(items)
        if not farmers:
            return False, "No grouped items to send."

        context_line = {
            'confirmed': "Please visit your dashboard to complete payment and track your order.",
            'rejected': "We're sorry, your order could not be fulfilled. You can browse other listings on FarmArt.",
            'pending': "Your order is currently pending. We'll notify you as soon as it progresses."
        }.get(status, "")

        order_lines = format_order_lines([item for farmer in farmers for item in farmer.get('items', [])])

        msg = Message(
            subject="FARMART - Order Status Update",
            sender="farmart597@gmail.com",
            recipients=[user.email]
        )
        msg.body = (
            f"Hello {user.username},\n\n"
            f"We wanted to update you on your recent order. The status has been marked as *{status.upper()}*.\n\n"
            f"Order Summary:{order_lines}\n"
            f"{context_line}\n\n"
            f"If you have any questions, feel free to contact us.\n\n"
            f"Thank you for using FarmArt!\n"
            f"Let’s keep farming digital 🌱"
        )

        mail.send(msg)
        return True, "Email sent to user."

    except Exception as e:
        return False, str(e)

def send_status_update_to_farmers(data):
    try:
        status = data.get('status', '').lower()
        items = data.get('items', [])

        if not status or not items:
            return False, "Missing status or items."

        farmers = group_items_by_farmer_util(items)
        if not farmers:
            return False, "No grouped items for farmers."

        context_line = {
            'confirmed': "Please prepare the items for shipment. Expect user contact soon.",
            'rejected': "This order was rejected. Stay tuned for new incoming requests.",
            'pending': "The user has marked this order as pending. Please wait for further updates."
        }.get(status, "")

        for farmer in farmers:
            recipient_email = farmer.get('email')
            username = farmer.get('username')
            items = farmer.get('items', [])

            if not recipient_email or not items:
                continue

            order_lines = format_order_lines(items)

            msg = Message(
                subject="FARMART - Order Status Notification",
                sender="farmart597@gmail.com",
                recipients=[recipient_email]
            )
            msg.body = (
                f"Hello {username},\n\n"
                f"This is to confirm that you have changed status of the following order to *{status.upper()}*.\n\n and that the customer has also been informed "
                f"Order Summary:{order_lines}\n"
                f"{context_line}\n\n"
                f"Thank you for being part of FarmArt!\n"
                f"Together, we’re growing something great 🌱🚜"
            )

            mail.send(msg)

        return True, "Emails sent to farmers."

    except Exception as e:
        return False, str(e)


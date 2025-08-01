from flask_mail import Message
from flask import current_app
from App.extensions import mail
from App.models.Users import User
from App.Utils.mail_utils import group_items_by_farmer_util


def format_order_lines(items: list[dict]) -> str:
    """Format a list of item dictionaries into readable order lines for email."""
    if not items:
        return ""

    return ''.join(
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
        for item in items
    )


def send_status_update_to_user(data: dict) -> tuple[bool, str]:
    """Send order status update email to a user."""
    user_id = data.get('user_id')
    status = data.get('status', '').lower()
    items = data.get('items', [])

    if not user_id or not status or not items:
        return False, "Missing user_id, status, or items."

    user = User.query.get(user_id)
    if not user:
        return False, "User not found."

    grouped_items = group_items_by_farmer_util(items)
    if not grouped_items:
        return False, "No grouped items to send."

    all_items = [item for farmer in grouped_items for item in farmer.get('items', [])]
    order_summary = format_order_lines(all_items)

    status_messages = {
        'confirmed': "Please visit your dashboard to complete payment and track your order.",
        'rejected': "We're sorry, your order could not be fulfilled. You can browse other listings on FarmArt.",
        'pending': "Your order is currently pending. We'll notify you as soon as it progresses."
    }

    message_body = (
        f"Hello {user.username},\n\n"
        f"We wanted to update you on your recent order. "
        f"The status has been marked as *{status.upper()}*.\n\n"
        f"Order Summary:{order_summary}\n"
        f"{status_messages.get(status, '')}\n\n"
        f"If you have any questions, feel free to contact us.\n\n"
        f"Thank you for using FarmArt!\n"
        f"Let’s keep farming digital 🌱"
    )

    try:
        msg = Message(
            subject="FARMART - Order Status Update",
            sender="farmart597@gmail.com",
            recipients=[user.email],
            body=message_body
        )
        mail.send(msg)
        return True, "Email sent to user."
    except Exception as e:
        current_app.logger.error(f"[MAIL][USER] {str(e)}")
        return False, f"Error sending user email: {str(e)}"


def send_status_update_to_farmers(data: dict) -> tuple[bool, str]:
    """Send order status update email to relevant farmers."""
    status = data.get('status', '').lower()
    items = data.get('items', [])

    if not status or not items:
        return False, "Missing status or items."

    grouped_items = group_items_by_farmer_util(items)
    if not grouped_items:
        return False, "No grouped items for farmers."

    status_messages = {
        'confirmed': "Please prepare the items for shipment. Expect user contact soon.",
        'rejected': "This order was rejected. Stay tuned for new incoming requests.",
        'pending': "The user has marked this order as pending. Please wait for further updates."
    }

    errors = []
    for farmer in grouped_items:
        email = farmer.get('email')
        username = farmer.get('username')
        farmer_items = farmer.get('items', [])

        if not email or not farmer_items:
            continue

        order_summary = format_order_lines(farmer_items)

        message_body = (
            f"Hello {username},\n\n"
            f"This is to confirm that you have changed the status of the following order to *{status.upper()}*.\n\n"
            f"The customer has also been notified.\n\n"
            f"Order Summary:{order_summary}\n"
            f"{status_messages.get(status, '')}\n\n"
            f"Thank you for being part of FarmArt!\n"
            f"Together, we’re growing something great 🌱🚜"
        )

        try:
            msg = Message(
                subject="FARMART - Order Status Notification",
                sender="farmart597@gmail.com",
                recipients=[email],
                body=message_body
            )
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f"[MAIL][FARMER][{email}] {str(e)}")
            errors.append(str(e))

    if errors:
        return False, "Some farmer emails failed. Check logs for details."

    return True, "Emails sent to all farmers."

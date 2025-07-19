
from flask_mail import Message
from App import mail
from App.Utils.mail_utils import group_items_by_farmer_util, validate_request_data, compose_order_lines, send_email, get_user_contact 
from App.Utils.Mail_compose_utils import compose_Order_email_to_farmer
 

def send_order_confirmation_to_user(user_id, order_id, created_at, amount, items):
    number = len(items)
    recipient = get_user_contact(user_id)
    email = recipient['email']
    username = recipient['username']

    farmers = group_items_by_farmer_util(items)

    detailed_lines = ""
    for farmer in farmers:
        farmer_email = farmer.get('email')
        farmer_username = farmer.get('username')
        f_items = farmer.get('items', [])

        detailed_lines += f"\nFarmer: {farmer_username} ({farmer_email})\n"
        detailed_lines += "-" * 40 + "\n"
        for item in f_items:
            detailed_lines += f"""Animal: {item.get('name')}
Type: {item.get('type')}
Breed: {item.get('breed')}
Age: {item.get('age')}
Price: KES {item.get('price_at_order_time')}
Quantity: {item.get('quantity')}
Available: {"Yes" if item.get('is_available') else "No"}
Description: {item.get('description')}
Images Listed: {item.get('image_count')}

"""

    msg = Message(
        subject='FARMART - Order Confirmation',
        sender='farmart597@gmail.com',
        recipients=[email]
    )

    msg.body = (
        f"Hello {username},\n\n"
        f"This is to confirm your order **{order_id}**, placed on {created_at}.\n"
        f"Total Amount: KES {amount}\n"
        f"Total Items: {number}\n\n"
        f"The following animals have been ordered:\n"
        f"{detailed_lines}\n"
        f"A confirmation email has been sent to the farmer(s). "
        f"You'll receive another message once they confirm so you can proceed with payment and delivery.\n\n"
        f"HAPPY SHOPPING!\nFARMART TEAM 🌱"
    )

    try:
        mail.send(msg)
        return True, None
    except Exception as e:
        return False, str(e)


def send_order_confirmation_to_farmers(items):
    farmers = group_items_by_farmer_util(items)
    failed_emails = []
    successful_emails = []

    for farmer in farmers:
        recipient_email = farmer.get('email')
        username = farmer.get('username')
        f_items = farmer.get('items', [])

        if not recipient_email or not f_items:
            continue

        order_lines = compose_order_lines(f_items)
        msg = compose_Order_email_to_farmer(recipient_email, username, order_lines)

        sent, error = send_email(msg, recipient_email)

        if sent:
            successful_emails.append(recipient_email)
        else:
            failed_emails.append({'email': recipient_email, 'error': error})

    return successful_emails, failed_emails

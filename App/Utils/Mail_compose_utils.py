from flask_mail import Message


def compose_Order_email_to_farmer(recipient_email, username, order_lines):
    msg = Message(
        subject='FARMART - New Animal Order Received',
        sender='farmart597@gmail.com',
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
    return msg



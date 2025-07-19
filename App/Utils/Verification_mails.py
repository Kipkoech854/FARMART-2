from flask_mail import Message
from App.extensions import mail


def send_verification_email(email, username, verify_url):
    msg = Message(
        subject='Verify your FarmArt Account',
        recipients=[email],
        sender='arvinkipo@gmail.com'
    )
    msg.body = f"""
Hello {username},

Thank you for registering at FarmArt.

Please click the link below to verify your email address and activate your account:

{verify_url}

This link is valid for 1 hour.

If you did not register, please ignore this email.

- The FarmArt Team
"""
    mail.send(msg)


def send_welcome_email(to_email, username):
    subject = "Welcome to Farmart!"
    body = f"""Hello {username},

🎉 Your account has been successfully verified!

We're excited to have you on board. You can now log in and start exploring everything we offer.

If you ever need help, feel free to reach out.

Best regards,  
The Farmart Team
"""
    msg = Message(subject=subject, recipients=[to_email], body=body)
    mail.send(msg)


def send_farmer_welcome_email(to_email, username):
    subject = "🎉 Welcome to Farmart!"
    body = f"""Hello {username},

Your farmer account has been successfully verified! ✅

You're now ready to list animals, manage your farm profile, and connect with buyers.

If you need assistance, our team is here to help.

Happy Farming!  
- The Farmart Team
"""
    msg = Message(subject=subject, recipients=[to_email], body=body)
    mail.send(msg)    
from flask import Blueprint,jsonify,request
from flask_mail import Message
from App.extensions import mail
import requests
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_mail import Message

Auth_Mail_bp = Blueprint('Auth_Mail_bp', __name__)

@Auth_Mail_bp.route('/VerificationMail-User', methods = ["POST"])
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

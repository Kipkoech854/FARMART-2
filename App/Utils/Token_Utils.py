from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def generate_verification_token(data: dict) -> str:
    """Generate token with full registration data."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(data, salt='email-confirm')

def confirm_verification_token(token: str, expiration=3600) -> dict:
    """Decode token and return embedded user data."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.loads(token, salt='email-confirm', max_age=expiration)

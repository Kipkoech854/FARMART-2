import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:kihikah@localhost:5432/farmart_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your_jwt_secret_key'

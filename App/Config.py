import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:kihikah@localhost:5432/farmart_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'


from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from .Config import config_by_name
from App.extensions import ma, db
from App.models import *
from App.extensions import mail
from dotenv import load_dotenv
import os  # Ensures all models are registered

# Only define new extensions if they're not already in extensions.py
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
load_dotenv()

def create_app(config_name='development'):
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config_by_name[config_name])
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')


    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    mail.init_app(app)

    # Create all tables after models are loaded
   
    with app.app_context():
        db.create_all()

    # Register blueprints
    from .routes.order_routes import Order_bp
    from .routes.Mail_routes import Mail_bp

    app.register_blueprint(Order_bp, url_prefix='/api/Order')
    app.register_blueprint(Mail_bp, url_prefix='/api/Mail')

    return app

from flask import Flask
from dotenv import load_dotenv
import os
from datetime import timedelta

from App.extensions import db, ma, migrate, jwt, cors, mail, bcrypt
from flask_jwt_extended import JWTManager
from .Config import config_by_name
from flask_cors import CORS

import smtplib

# Load .env from App folder explicitly
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "production")  # Default to production

    app = Flask(__name__)

    # Common configs
    app.config['MAIL_DEBUG'] = True
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    # Load environment-specific config (production/development/testing)
    app.config.from_object(config_by_name[config_name])
    print(app.config['SQLALCHEMY_DATABASE_URI'])

    # Mail config
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_SUPPRESS_SEND'] = False

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, supports_credentials=True)

    mail.init_app(app)
    bcrypt.init_app(app)

    with app.app_context():
        db.create_all()

    # Register blueprints
    from .routes.order_routes import Order_bp
    from .routes.animal import animals_blueprint
    from .routes.Auth_routes import auth_bp
    from .routes.Farmer_routes import farmer_routes
    from .routes.User_routes import user_bp
    from .routes.Mail_service_routes import Mailservice_bp
    from .routes.Auth_mail_routes import Auth_Mail_bp 
    from .routes.home_routes import home_bp 
    from .routes.Payment_routes import payment_bp 


    app.register_blueprint(home_bp) 
    app.register_blueprint(Order_bp, url_prefix='/api/Order')
    app.register_blueprint(animals_blueprint, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(farmer_routes, url_prefix='/api/farmers')
    app.register_blueprint(user_bp, url_prefix='/api/User')
    app.register_blueprint(Mailservice_bp, url_prefix='/api/Mailservice')
    app.register_blueprint(Auth_Mail_bp, url_prefix='/api/AuthMail')
    app.register_blueprint(payment_bp, url_prefix='/api/Payment')


    return app
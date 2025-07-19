from flask import Flask
from dotenv import load_dotenv
import os
from datetime import timedelta

from App.extensions import db, ma, migrate, jwt, cors, mail, bcrypt
from flask_jwt_extended import JWTManager
from .Config import config_by_name

import smtplib

# Load .env from App folder explicitly
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

def create_app(config_name='testing'):
    app = Flask(__name__)

    app.config['MAIL_DEBUG'] = True
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


    # Load configuration
    app.config.from_object(config_by_name[config_name])
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    app.config['MAIL_USE_SSL'] = False  # or True if using port 465
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_SUPPRESS_SEND'] = False
 
    

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)

    with app.app_context():
        db.create_all()

    # Register blueprints
    from .routes.order_routes import Order_bp
    from .routes.Mail_routes import Mail_bp
    from .routes.animal import animals_blueprint
    from .routes.Auth_routes import auth_bp
    from .routes.Farmer_routes import farmer_routes
    from .routes.User_routes import user_bp
    from .routes.Mail_service_routes import Mailservice_bp
    from .routes.Status_mail_routes import Status_mail_bp
    from .routes.Delivery_mail_routes import Delivery_mail_bp 
    from .routes.Auth_mail_routes import Auth_Mail_bp 

    app.register_blueprint(Order_bp, url_prefix='/api/Order')
    app.register_blueprint(Mail_bp, url_prefix='/api/Mail')
    app.register_blueprint(animals_blueprint, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(farmer_routes, url_prefix='/api/farmers')
    app.register_blueprint(user_bp, url_prefix='/api/User')
    app.register_blueprint(Mailservice_bp, url_prefix='/api/Mailservice')
    app.register_blueprint(Status_mail_bp, url_prefix='/api/StatusMail')
    app.register_blueprint(Delivery_mail_bp, url_prefix='/api/DeliveryMail')
    app.register_blueprint(Auth_Mail_bp, url_prefix='/api/AuthMail')

    return app

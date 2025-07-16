from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from .Config import config_by_name
from App.extensions import ma, db
from App.models import *  # Ensures all models are registered

# Only define new extensions if they're not already in extensions.py
migrate = Migrate()
jwt = JWTManager()
cors = CORS()

def create_app(config_name='development'):
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)

    # Create all tables after models are loaded
   
    with app.app_context():
        db.create_all()

    # Register blueprints
    from .routes.order_routes import Order_bp
    app.register_blueprint(Order_bp, url_prefix='/api')

    return app

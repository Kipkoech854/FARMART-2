from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from .Config import config_by_name
from App.extensions import ma,db



db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors= CORS()

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Load configuration from a config file or object
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)

    # Register blueprints or routes here
    from . import models  # Assuming you have a routes module
    # from .routes import main as main_blueprint
    from .routes.order_routes import Order_bp 
    # app.register_blueprint(main_blueprint)

    app.register_blueprint(Order_bp, url_prefix = '/api')

    return app
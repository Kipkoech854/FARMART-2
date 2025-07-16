from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from App.Config import config_by_name


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
    jwt.init_app(app)
    cors.init_app(app)

    # Register blueprints or routes here
    from App import models  # Assuming you have a routes module
    # from .routes import main as main_blueprint
    from App.routes.Auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth') 
    # app.register_blueprint(main_blueprint)

    return app
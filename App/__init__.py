from flask import Flask
from .extensions import db, migrate, jwt, cors
from .Config import config_by_name

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)


    from .routes.animal import animals_blueprint
    app.register_blueprint(animals_blueprint, url_prefix='/api')

    # Register blueprints or routes here
    from App import models  # Assuming you have a routes module
    # from .routes import main as main_blueprint
    from App.routes.Auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth') 
    # app.register_blueprint(main_blueprint)


    return app
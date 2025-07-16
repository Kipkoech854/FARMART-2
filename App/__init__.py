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

    return app
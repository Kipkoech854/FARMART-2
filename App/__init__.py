from flask import Flask
from App.extensions import db, bcrypt
from flask_jwt_extended import JWTManager

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('App.Config.Config')

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app) 

    with app.app_context():
        from App import models  

    from App.routes.Farmer_routes import farmer_routes
    app.register_blueprint(farmer_routes)

    return app

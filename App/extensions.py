from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_mail import Mail
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
ma = Marshmallow()
mail = Mail()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
bcrypt = Bcrypt()

from flask import Blueprint

animals_blueprint = Blueprint('animals', __name__)


from .animal import animals_blueprint

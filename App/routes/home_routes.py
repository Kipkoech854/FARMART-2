from flask import Blueprint

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    return {"message": "Welcome to the Farmart API!"}

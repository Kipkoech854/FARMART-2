from flask import Flask
from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

Order_bp = Blueprint('Order_bp', __name__, template_folder='templates') 

app = Flask(__name__)

@Order_bp.route('/')
def Orders():
    return ('Orders')


 

if __name__ == 'main':
    app.run(debug = True)
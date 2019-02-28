from flask import Blueprint
from flask_cors import CORS

user = Blueprint('user', __name__, url_prefix='/api/v1/user')
CORS(user)

from . import Login

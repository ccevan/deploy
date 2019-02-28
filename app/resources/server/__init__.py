from flask import Blueprint
from flask_cors import CORS

server = Blueprint('server', __name__, url_prefix='/api/v1/server')
CORS(server)

from . import ServerApi
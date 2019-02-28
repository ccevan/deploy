from flask import Blueprint
from flask_cors import CORS

service = Blueprint('file', __name__, url_prefix='/api/v1/service')
CORS(service)

# from . import camera_platform, camera, organizations, channel
# from . import groups, camera_list
from . import ServiceApi
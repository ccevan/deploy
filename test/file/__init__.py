from flask import Blueprint
from flask_cors import CORS

file = Blueprint('file', __name__, url_prefix='/api/v1/file')
CORS(file)

# from . import camera_platform, camera, organizations, channel
# from . import groups, camera_list
from . import FileApi
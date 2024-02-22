from flask import Blueprint
import logging

# API Blueprint
authentication_api_bp = Blueprint('authentication', __name__)

# API Logger configuration
authentication_api_logger = logging.getLogger('authentication_api')
authentication_api_logger.setLevel(logging.DEBUG)
authentication_api_logger.addHandler(logging.FileHandler('logs/authentication_api.log'))

from . import routes
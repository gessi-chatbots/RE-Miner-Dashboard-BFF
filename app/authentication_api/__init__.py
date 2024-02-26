from flask import Blueprint
from datetime import datetime
import logging

# API Blueprint
authentication_api_bp = Blueprint('authentication', __name__)

# API Logger configuration
authentication_api_logger = logging.getLogger('authentication_api')
authentication_api_logger.setLevel(logging.DEBUG)
authentication_api_logger.addHandler(logging.FileHandler(f'logs/[{datetime.now().date()}]authentication_api.log'))


from . import routes
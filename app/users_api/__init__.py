from flask import Blueprint
import logging

users_api_bp = Blueprint('users_api', __name__)

# API Logger configuration
users_api_logger = logging.getLogger('users_api')
users_api_logger.setLevel(logging.DEBUG)
users_api_logger.addHandler(logging.FileHandler('logs/users_api.log'))

from . import routes, models

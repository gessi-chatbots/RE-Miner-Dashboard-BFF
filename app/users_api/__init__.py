from flask import Blueprint
import logging

users_api_bp = Blueprint('users_api', __name__)

# API Logger configuration
users_api_logger = logging.getLogger('users_api')
users_api_logger.setLevel(logging.DEBUG)
users_api_logger.addHandler(logging.FileHandler('logs/users_api.log'))

class UnknownException(Exception):
    code = 500
    message = "Unexpected server error"

class UserNotFound(Exception):
    code = 404
    message = "User not found"

class UserIntegrityException(Exception):
    code = 400
    message = "An User with the given email is already registered"

from . import routes, models

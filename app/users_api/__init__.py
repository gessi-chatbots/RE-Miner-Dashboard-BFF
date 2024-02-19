from flask import Blueprint
import logging

users_api_bp = Blueprint('users_api', __name__)

users_api_logger = logging.getLogger('users_api')
users_api_logger.setLevel(logging.DEBUG)


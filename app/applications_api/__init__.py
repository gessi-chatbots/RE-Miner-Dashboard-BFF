from flask import Blueprint
import logging

reviews_api_bp = Blueprint('applications_api', __name__)

# API Logger configuration
reviews_api_logger = logging.getLogger('applications_api')
reviews_api_logger.setLevel(logging.DEBUG)
reviews_api_logger.addHandler(logging.FileHandler('logs/applications_api.log'))

from . import routes, models

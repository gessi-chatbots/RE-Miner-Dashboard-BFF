from flask import Blueprint
import logging

reviews_api_bp = Blueprint('reviews_api', __name__)

# API Logger configuration
reviews_api_logger = logging.getLogger('reviews_api')
reviews_api_logger.setLevel(logging.DEBUG)
reviews_api_logger.addHandler(logging.FileHandler('logs/reviews_api.log'))

from . import routes, models

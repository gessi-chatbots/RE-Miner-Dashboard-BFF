from flask import Blueprint
import logging

# API Blueprint
applications_api_bp = Blueprint('applications_api', __name__)

# API Logger configuration
applications_api_logger = logging.getLogger('applications_api')
applications_api_logger.setLevel(logging.DEBUG)
applications_api_logger.addHandler(logging.FileHandler('logs/applications_api.log'))

from . import forms, routes

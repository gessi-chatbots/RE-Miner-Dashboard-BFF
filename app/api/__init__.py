from flask import Blueprint
from datetime import datetime
import logging
from app import jwt

# API Blueprint
api_bp = Blueprint('api', __name__)

# API Logger configuration
api_logger = logging.getLogger('api')
api_logger.setLevel(logging.DEBUG)
api_logger.addHandler(logging.FileHandler(f'logs/[{datetime.now().date()}]api.log'))

# JWT Loader and Lookup
import app.users_api.service as users_api_service
@jwt.user_identity_loader
def user_identity_lookup(id):
    user = users_api_service.get_user_by_id(id)
    return user.id
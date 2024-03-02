import os
import logging
import secrets
from flask import Flask, Blueprint
from flask_jwt_extended import JWTManager
from datetime import datetime, timedelta

# API configuration
api = Flask(__name__)
api.config['SECRET_KEY'] = secrets.token_hex(16)
api.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URL', 'postgresql://postgres:pg_strong_password@localhost:5432/dashboard_db')
print(f"Database URI: {api.config['SQLALCHEMY_DATABASE_URI']}")
api.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# API version
api_name = 'api'
api_version = 'v1'
# API Blueprint
api_bp = Blueprint('api_name', __name__, url_prefix=f'/{api_name}/{api_version}')

# JWT Configuration
api.config["JWT_COOKIE_SECURE"] = True
api.config["JWT_TOKEN_LOCATION"] = ["cookies"]
api.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
api.config['JWT_ACCESS_COOKIE_PATH'] = f'/{api_name}/{api_version}'
api.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
api.config['JWT_REFRESH_COOKIE_PATH'] = f'/{api_name}/{api_version}/refresh'
api.config['JWT_COOKIE_CSRF_PROTECT'] = False
api.config["JWT_SECRET_KEY"] = secrets.token_hex(16)
jwt = JWTManager(api)

# DB integration
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(api)

# Schema generation 
# (it could be done via migration, but as we have a simple schema we hardcode it)
from api.models import User, Application, Review
with api.app_context():
    db.create_all()

# API Logger configuration
api_logger = logging.getLogger('api')
api_logger.setLevel(logging.DEBUG)
api_logger.addHandler(logging.FileHandler(f'logs/[{datetime.now().date()}]api.log'))

# JWT Loader and Lookup
import api.service.user_service as users_api_service
@jwt.user_identity_loader
def user_identity_lookup(id):
    user = users_api_service.get_user_by_id(id)
    return user.id
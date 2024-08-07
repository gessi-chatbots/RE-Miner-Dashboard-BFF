import secrets
import os
import nltk
from flask import Flask
from flask_jwt_extended import JWTManager
from datetime import timedelta
from tenacity import retry, stop_after_delay, wait_fixed

nltk.download('punkt')

# App configuration
api = Flask(__name__)

from flask_cors import CORS
CORS(api, supports_credentials=True, origins='http://localhost:3000')

api.config['SECRET_KEY'] = secrets.token_hex(16)
api.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URL', 'postgresql://postgres:pg_strong_password@localhost:5432/dashboard_db')
api.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api.config['CORS_HEADERS'] = 'Content-Type'

# APIs Versions
api_version = 'v1'

# JWT Configuration
api.config["JWT_COOKIE_SECURE"] = False
api.config["JWT_TOKEN_LOCATION"] = ["cookies"]
api.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
api.config['JWT_ACCESS_COOKIE_PATH'] = f'/api/{api_version}'
api.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
api.config['JWT_REFRESH_COOKIE_PATH'] = f'/api/{api_version}/refresh'
api.config['JWT_COOKIE_CSRF_PROTECT'] = False
api.config["JWT_SECRET_KEY"] = secrets.token_hex(16)
jwt = JWTManager(api)

# DB integration
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(api)


# APIs blueprints registration
from api.routes import api_bp
api.register_blueprint(api_bp, url_prefix=f'/api/{api_version}')

# Schema generation 
# (it could be done via migration, but as we have a simple schema we hardcode it)
@retry(stop=stop_after_delay(60), wait=wait_fixed(3))
def connect_to_db():
    from api.models import User
    from api.models import Application
    from api.models import Review
    try:
        with api.app_context():
            db.create_all()
            return True
    except Exception as e:
        raise

connect_to_db()
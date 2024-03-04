import secrets
from flask import Flask
from flask_jwt_extended import JWTManager
from datetime import timedelta
import os
from tenacity import retry, stop_after_delay, wait_fixed

# App configuration
api = Flask(__name__)
api.config['SECRET_KEY'] = secrets.token_hex(16)
api.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URL', 'postgresql://postgres:pg_strong_password@localhost:5432/dashboard_db')
print(f"Database URI: {api.config['SQLALCHEMY_DATABASE_URI']}")
api.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
@retry(stop=stop_after_delay(30), wait=wait_fixed(2))
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
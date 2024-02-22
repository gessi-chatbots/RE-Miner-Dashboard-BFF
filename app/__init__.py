import secrets
from flask import Flask, Blueprint
from datetime import timedelta
import os


# App configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URL', 'postgresql://postgres:pg_strong_password@localhost:5433/dashboard_db')
print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Token Management
app.config["JWT_COOKIE_SECURE"] = True
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_SECRET_KEY"] = secrets.token_hex(16)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
from flask_jwt_extended import JWTManager
jwt = JWTManager(app)

# DB integration
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

# APIs blueprints registration
from app.users_api.routes import users_api_bp
app.register_blueprint(users_api_bp, url_prefix='/users_api')

from app.reviews_api.routes import reviews_api_bp
app.register_blueprint(reviews_api_bp, url_prefix='/reviews_api')

from app.applications_api.routes import applications_api_bp
app.register_blueprint(applications_api_bp, url_prefix='/applications_api')

from app.authentication_api.routes import authentication_api_bp
app.register_blueprint(authentication_api_bp)

# Schema generation 
# (it could be done via migration, but as we have a simple schema we hardcode it)
from app.users_api.models import User
from app.applications_api.models import Application
from app.reviews_api.models import Review
with app.app_context():
    db.create_all()
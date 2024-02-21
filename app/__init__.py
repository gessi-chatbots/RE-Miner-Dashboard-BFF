import secrets
from flask import Flask
import os

# App configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URL', 'postgresql://postgres:pg_strong_password@localhost:5433/dashboard_db')
print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# DB integration
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

from app.exceptions import UnknownException, UserNotFound

# APIs blueprints registration
from app.users_api.routes import users_api_bp
app.register_blueprint(users_api_bp, url_prefix='/users_api')

from app.reviews_api.routes import reviews_api_bp
app.register_blueprint(reviews_api_bp, url_prefix='/reviews_api')

from app.applications_api.routes import applications_api_bp
app.register_blueprint(applications_api_bp, url_prefix='/applications_api')



# Schema generation 
# (it could be done via migration, but as we have a simple schema we hardcode it)
from app.users_api.models import User
from app.applications_api.models import Application
from app.reviews_api.models import Review
with app.app_context():
    db.create_all()
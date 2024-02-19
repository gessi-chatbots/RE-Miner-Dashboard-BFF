import secrets
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.users_api.routes import users_api_bp
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin@re-miner-dashboard-db/RE_Miner_Dashboard_DB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemy initialization with the app
database = SQLAlchemy(app)

# APIs blueprints registrations
app.register_blueprint(users_api_bp, url_prefix='/users_api')

from app.users_api import models
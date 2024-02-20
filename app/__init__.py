import secrets
from flask import Flask
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URL', 'postgresql://postgres:pg_strong_password@localhost:5433/dashboard_db')
print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# APIs blueprints registrations
from app.users_api.routes import users_api_bp
app.register_blueprint(users_api_bp, url_prefix='/users_api')

from app.users_api.models import User
with app.app_context():
    db.create_all()
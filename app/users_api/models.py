from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

database = SQLAlchemy()

class User(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(50), nullable=False)
    family_name = database.Column(database.String(50), nullable=False)
    email = database.Column(database.String(50), unique=True, nullable=False)

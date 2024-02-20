from flask_login import UserMixin
from app import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    family_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)

    def json(self):
        return {'id': self.id,
                'name': self.name, 
                'family_name': self.family_name,
                'email': self.email}


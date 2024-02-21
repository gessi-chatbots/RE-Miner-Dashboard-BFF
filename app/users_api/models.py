from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

user_application_association = db.Table(
    'user_applications',
    db.Column('user_id', db.String(36), db.ForeignKey('users.id')),
    db.Column('application_name', db.String, db.ForeignKey('applications.name'))
)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    family_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    @property
    def password(self):
        raise AttributeError('password not readable')

    @password.setter
    def password(self, plaintext_password):
        self.password_hash = generate_password_hash(plaintext_password)

    def check_password(self, plaintext_password):
        return check_password_hash(self.password_hash, plaintext_password)
    
    applications = db.relationship(
        'Application',
        secondary=user_application_association,
        backref=db.backref('users', lazy='dynamic'),
        lazy='dynamic'
    )

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'family_name': self.family_name,
            'email': self.email
        }



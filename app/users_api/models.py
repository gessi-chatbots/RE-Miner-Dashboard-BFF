from app import db
from flask_login import UserMixin

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



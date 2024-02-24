from app import db
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, Email
user_application_association = db.Table(
    'user_applications',
    db.Column('user_id', db.String(36), db.ForeignKey('users.id')),
    db.Column('application_name', db.String, db.ForeignKey('applications.name'))
)

class RegistrationForm(FlaskForm):
    name = StringField('name', validators=[InputRequired(), Length(min=1, max=30)])
    family_name = StringField('family_name', validators=[InputRequired(), Length(min=1, max=30)])
    email = StringField('email', validators=[InputRequired(), Length(min=5), Email()])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=30)])
    
    # Excluding CSRF Token field (we are using JWT)
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        delattr(self, 'csrf_token')

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



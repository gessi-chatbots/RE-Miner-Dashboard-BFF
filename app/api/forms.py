from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, Email

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Length(min=5), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=30)])
    
    # Excluding CSRF Token field (we are using JWT)
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        delattr(self, 'csrf_token')

class RegistrationForm(FlaskForm):
    name = StringField('name', validators=[InputRequired(), Length(min=1, max=30)])
    family_name = StringField('family_name', validators=[InputRequired(), Length(min=1, max=30)])
    email = StringField('email', validators=[InputRequired(), Length(min=5), Email()])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=30)])
    
    # Excluding CSRF Token field (we are using JWT)
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        delattr(self, 'csrf_token')



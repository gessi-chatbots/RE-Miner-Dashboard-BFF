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
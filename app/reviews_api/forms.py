from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, Email

class ReviewForm(FlaskForm):
    reviewId = StringField('reviewId', validators=[InputRequired(), Length(min=1, max=30)])
    # Excluding CSRF Token field (we are using JWT)
    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        delattr(self, 'csrf_token')
    def to_dict(self):
        return {'reviewId': self.reviewId.data}


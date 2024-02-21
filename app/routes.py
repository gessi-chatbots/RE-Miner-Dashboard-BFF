from flask import request
from . import app
from users_api.authenticationService import check_valid_user
from flask_jwt_extended import create_access_token

@app.route('/login', methods=['GET', 'POST'])
def login():
    if check_valid_user(request.form):
        create_access_token(request.form.get('email'))
    
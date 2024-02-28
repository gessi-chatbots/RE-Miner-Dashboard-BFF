from flask import request, jsonify, make_response, abort
from app.authentication_api.service import (generate_access_token, 
                                            generate_refresh_token,
                                            refresh_access_token)
from app.users_api.service import check_valid_user
from app.authentication_api.forms import LoginForm
from . import authentication_api_bp, authentication_api_logger
from datetime import datetime
from flask_jwt_extended import (set_access_cookies, 
                                set_refresh_cookies, 
                                jwt_required,
                                get_jwt_identity,
                                unset_jwt_cookies)

def validate_login_form(form): 
    if not form.validate():
        errors = {"errors": []}
        for field, messages in form.errors.items():
            for error in messages:
                errors["errors"].append({"field": field, "message": error})
        return jsonify(errors), 400
    

@authentication_api_bp.route('/ping', methods=['GET'])
def ping():
    authentication_api_logger.info(f"[{datetime.now()}]: Ping Authentication API") 
    return make_response(jsonify({'message': 'Ping Authentication API ok'}), 200)

@authentication_api_bp.route('/login', methods=['POST'])
def login():
    authentication_api_logger.info(f"[{datetime.now()}]: Login User")
    # COMMENT THIS PART IF YOU WANT AUTHENTICATION WITHOUT USER VALIDATION
    # -------------------------------------------------------------------
    login_form = LoginForm(request.form)
    validate_login_form(login_form)
    email = login_form.email.data
    password = login_form.password.data
    if not check_valid_user(email, password):
        abort(401, description='Invalid credentials')
    # -------------------------------------------------------------------
    access_token = generate_access_token(email)
    refresh_token = generate_refresh_token(email)
    resp = jsonify({'login': True})
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp, 200

@authentication_api_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    authentication_api_logger.info(f"[{datetime.now()}]: Refresh token request") 
    resp = jsonify({'refresh': True})
    id = get_jwt_identity()
    authentication_api_logger.info(f"[{datetime.now()}]: Id: {id}") 
    set_access_cookies(resp, refresh_access_token(id))
    return resp, 200

@authentication_api_bp.route('/logout', methods=['POST'])
def logout():
    authentication_api_logger.info(f"[{datetime.now()}]: Logout") 
    resp = jsonify({'logout': True})
    unset_jwt_cookies(resp)
    return resp, 200
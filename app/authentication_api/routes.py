from flask import request, jsonify, make_response, abort
from .service import generate_access_token, generate_refresh_token
from app.users_api.service import check_valid_user
from . import authentication_api_bp, authentication_api_logger
from datetime import datetime
from flask_jwt_extended import (set_access_cookies, 
                                set_refresh_cookies, 
                                jwt_required,
                                get_jwt_identity,
                                unset_jwt_cookies)

@authentication_api_bp.route('/ping', methods=['GET'])
def ping():
    authentication_api_logger.info(f"[{datetime.now()}]: Ping Authentication API") 
    return make_response(jsonify({'message': 'Ping Authentication API ok'}), 200)

@authentication_api_bp.route('/login', methods=['POST'])
def login():
    authentication_api_logger.info(f"[{datetime.now()}]: Login User") 
    email = request.json.get("email", None)
    if email is None:
        abort(401, description='No email has been provided')

    password = request.json.get("password", None)
    if password is None:
        abort(401, description='No password has been provided')

    if not check_valid_user(email, password):
        abort(401, description='Invalid credentials')

    access_token = generate_access_token(email)
    refresh_token = generate_refresh_token(email)
    
    resp = jsonify({'login': True})
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp, 200

@authentication_api_bp.route('/token/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_access_token():
    authentication_api_logger.info(f"[{datetime.now()}]: Refresh token request") 
    resp = jsonify({'refresh': True})
    email = get_jwt_identity()
    authentication_api_logger.info(f"[{datetime.now()}]: Email: {email}") 
    set_access_cookies(resp, generate_access_token(email))
    return resp, 200

@authentication_api_bp.route('/logout', methods=['POST'])
def logout():
    authentication_api_logger.info(f"[{datetime.now()}]: Logout") 
    resp = jsonify({'logout': True})
    unset_jwt_cookies(resp)
    return resp, 200
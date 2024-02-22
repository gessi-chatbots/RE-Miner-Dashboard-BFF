from flask import request, jsonify, make_response, abort
from .service import generate_access_token, generate_refresh_token
from app.users_api.service import check_valid_user
from . import authentication_api_bp, authentication_api_logger
from datetime import datetime

@authentication_api_bp.route('/ping', methods=['GET'])
def ping():
    authentication_api_logger.info(f"[{datetime.now()}]: Ping Authentication API") 
    return make_response(jsonify({'message': 'Ping Authentication API ok'}), 200)

@authentication_api_bp.route('/login', methods=['POST'])
def login():
    email = request.json.get("email", None)
    if email is None:
        abort(400, description='No email has been provided')

    password = request.json.get("password", None)
    if password is None:
        abort(400, description='No password has been provided')

    if not check_valid_user(email, password):
        abort(401, description='Invalid credentials')

    access_token = generate_access_token(email)
    refresh_token = generate_refresh_token(email)
    
    response_data = {
        'access_token': access_token,
        'refresh_token': refresh_token
    }

    return make_response(jsonify(response_data), 200)

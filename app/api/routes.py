from . import api_bp, api_logger
from datetime import datetime
from flask import request, jsonify, make_response, abort
from flask_jwt_extended import (set_access_cookies, 
                                set_refresh_cookies, 
                                jwt_required,
                                get_jwt_identity,
                                unset_jwt_cookies)
import app.api.forms as api_forms
import app.api.utils as api_utils
import app.api.authentication_service as authentication_service
import app.api.user_service as user_service
import app.api.review_service as review_service
import app.api.application_service as application_service

@api_bp.route('/ping', methods=['GET'])
def ping():
    api_logger.info(f"[{datetime.now()}]: Ping API") 
    return make_response(jsonify({'message': 'API ok'}), 200)

# -------------- Authentication --------------
@api_bp.route('/login', methods=['POST'])
def login():
    api_logger.info(f"[{datetime.now()}]: Login User")
    login_form = api_forms.LoginForm(request.form)
    api_utils.validate_form(login_form)
    email = login_form.email.data
    password = login_form.password.data
    if not user_service.check_valid_user(email, password):
        abort(401, description='Invalid credentials')
    access_token = authentication_service.generate_access_token(email)
    refresh_token = authentication_service.generate_refresh_token(email)
    resp = jsonify({'login': True})
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp, 200

@api_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    api_logger.info(f"[{datetime.now()}]: Refresh token request") 
    resp = jsonify({'refresh': True})
    id = get_jwt_identity()
    set_access_cookies(resp, authentication_service.refresh_access_token(id))
    return resp, 200

@api_bp.route('/logout', methods=['POST'])
def logout():
    api_logger.info(f"[{datetime.now()}]: Logout") 
    resp = jsonify({'logout': True})
    unset_jwt_cookies(resp)
    return resp, 200

# -------------- User --------------

@api_bp.route("/users", methods=['POST'])
def create_user():
    api_logger.info(f"[{datetime.now()}]: Register User")
    registration_form = api_forms.RegistrationForm(request.form)
    if not registration_form.validate():
        errors = {"errors": []}
        for field, messages in registration_form.errors.items():
            for error in messages:
                errors["errors"].append({"field": field, "message": error})
        return jsonify(errors), 400
    
    user = user_service.create_user(request.form)
    return make_response(jsonify({'user_data': user }), 201)

@api_bp.route('/users/user/<string:id>', methods=['GET'])
@jwt_required()
def get_user(id):
    api_logger.info(f"[{datetime.now()}]: Get User {id}")
    user_id = get_jwt_identity()
    if id != user_id:
        return make_response(jsonify({'Unauthorized': 'Cannot retrieve data from another user'}), 401)
    user = user_service.get_user_by_id(id)
    if user is None:
        return make_response(jsonify({'Unauthorized': 'Invalid user'}), 401)
    return make_response(jsonify({'user': user.json()}), 200)

@api_bp.route('/users/user/<string:user_id>', methods=['PUT', 'POST'])
@jwt_required()
def update_user(user_id):
    api_logger.info(f"[{datetime.now()}]: Update User {user_id}")
    if request.form is None:
        return make_response(jsonify({'message': 'No User data provided'}), 400)
    jtw_id = get_jwt_identity()
    if jtw_id != user_id:
        return make_response(jsonify({'Unauthorized': 'Cannot update data from another user'}), 401)
    if user_service.get_user_by_id(user_id) is None:
        return make_response(jsonify({'Unauthorized': 'Invalid user'}), 401)
    user = user_service.update_user(user_id, request.form)
    return make_response(jsonify({'user_data': user}), 200)

@api_bp.route('/users/user/<string:user_id>', methods=['DELETE'])
@jwt_required()
def delete(user_id):
    api_logger.info(f"[{datetime.now()}]: Delete User {id}")
    jwt_id = get_jwt_identity()
    if jwt_id != user_id:
        return make_response(jsonify({'Unauthorized': 'Cannot update data from another user'}), 401)
    if user_service.get_user_by_id(user_id) is None:
        return make_response(jsonify({'Unauthorized': 'Invalid user'}), 401)
    user_service.delete_user(user_id)
    return make_response(jsonify({'message': 'user deleted'}), 200)

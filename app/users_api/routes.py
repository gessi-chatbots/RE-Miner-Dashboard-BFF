from flask import request, jsonify, make_response
from .. import jwt
from . import users_api_bp, users_api_logger, UserIntegrityException, UserNotFound, UnknownException
from datetime import datetime
from .service import create_user, get_user_by_email, update_user, delete_user
from flask_jwt_extended import jwt_required, current_user

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user
    
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    return get_user_by_email(jwt_data["sub"])

@users_api_bp.errorhandler(UserNotFound)
def handle_user_not_found(exception):
    users_api_logger.info(exception)
    return make_response(jsonify({'message': exception.message}), exception.code)

@users_api_bp.errorhandler(UnknownException)
def handle_user_not_found(exception):
    return make_response(jsonify({'message': exception.message}), exception.code)

@users_api_bp.errorhandler(UserIntegrityException)
def handle_integrity_error(exception):
    return make_response(jsonify({'message': exception.message}), exception.code)

@users_api_bp.route('/ping', methods=['GET'])
def ping():
    users_api_logger.info(f"[{datetime.now()}]: Ping Users API") 
    return make_response(jsonify({'message': 'Ping Users API ok'}), 200)

@users_api_bp.route("/", methods=['POST'])
def create():
    users_api_logger.info(f"[{datetime.now()}]: Register User")
    if request.form is None:
        return make_response(jsonify({'message': 'No form data has been provided' }), 400)
    if request.form.get('password') is None: 
        return make_response(jsonify({'message': 'No password has been provided' }), 400)
    if request.form.get('email') is None: 
        return make_response(jsonify({'message': 'No email has been provided' }), 400)
    user = create_user(request.form)
    return make_response(jsonify({'user_data': user }), 201)

@users_api_bp.route('/user/<string:email>', methods=['GET'])
def get(email):
    users_api_logger.info(f"[{datetime.now()}]: Get User {email}") 
    user = get_user_by_email(email)
    return make_response(jsonify({'user': user.json()}), 200)

@users_api_bp.route('/user/<string:email>', methods=['PUT', 'POST'])
@jwt_required()
def update(email):
    users_api_logger.info(f"[{datetime.now()}]: Update User {id}")
    if request.form is None:
        return make_response(jsonify({'message': 'No User data provided'}), 400)
    user = update_user(email, request.form)
    return make_response(jsonify({'user_data': user}), 200)

@users_api_bp.route('/user/<string:id>', methods=['DELETE'])
def delete(id):
    users_api_logger.info(f"[{datetime.now()}]: Delete User {id}") 
    delete_user(id)
    return make_response(jsonify({'message': 'user deleted'}), 200)

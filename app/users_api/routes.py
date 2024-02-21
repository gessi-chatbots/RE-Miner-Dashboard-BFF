from flask import request, jsonify, make_response
from . import users_api_bp, users_api_logger, UserIntegrityException, UserNotFound, UnknownException
from datetime import datetime
from .userService import create_user, get_user, update_user, delete_user

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

@users_api_bp.route("/users", methods=['POST'])
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

@users_api_bp.route('/users/user/<string:id>', methods=['GET'])
def get(id):
    users_api_logger.info(f"[{datetime.now()}]: Get User {id}") 
    user = get_user(id)
    return make_response(jsonify({'user': user}), 200)

@users_api_bp.route('/users/user/<string:id>', methods=['PUT', 'POST'])
def update(id):
    users_api_logger.info(f"[{datetime.now()}]: Update User {id}")
    if request.form is None:
        return make_response(jsonify({'message': 'No User data provided'}), 400)
    user = update_user(id, request.form)
    return make_response(jsonify({'user_data': user}), 200)

@users_api_bp.route('/users/user/<string:id>', methods=['DELETE'])
def delete(id):
    users_api_logger.info(f"[{datetime.now()}]: Delete User {id}") 
    delete_user(id)
    return make_response(jsonify({'message': 'user deleted'}), 200)

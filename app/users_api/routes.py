from flask import request, jsonify, make_response
from . import users_api_bp, users_api_logger, UserIntegrityException, UserNotFound, UnknownException
from datetime import datetime
from .service import create_user, get_user, update_user, delete_user

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
    user_data = create_user(request)
    return make_response(jsonify({'user_data': user_data }), 201)

@users_api_bp.route('/users/user/<string:id>', methods=['GET'])
def get(id):
    users_api_logger.info(f"[{datetime.now()}]: Get User {id}") 
    user = get_user(id)
    return make_response(jsonify({'user': user.json()}), 200)

@users_api_bp.route('/users/user/<string:id>', methods=['PUT', 'POST'])
def update(id):
    users_api_logger.info(f"[{datetime.now()}]: Update User {id}")
    if request.form is None:
        return make_response(jsonify({'message': 'No User data provided'}), 400)
    user = update_user(id, request.form)
    return make_response(jsonify({'user_data': user.json()}), 200)

@users_api_bp.route('/users/user/<string:id>', methods=['DELETE'])
def delete(id):
    users_api_logger.info(f"[{datetime.now()}]: Delete User {id}") 
    delete_user(id)
    return make_response(jsonify({'message': 'user deleted'}), 200)

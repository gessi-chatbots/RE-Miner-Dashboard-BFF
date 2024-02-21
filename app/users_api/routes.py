from flask import request, jsonify, make_response, abort
from . import users_api_bp, users_api_logger, UserNotFound, UnknownException
from datetime import datetime
from .service import create_user, get_user, update_user, delete_user

@users_api_bp.errorhandler(UserNotFound)
def handle_user_not_found(exception):
    users_api_logger.info(exception)
    return make_response(jsonify({'message': exception.message}), exception.code)

@users_api_bp.errorhandler(UnknownException)
def handle_user_not_found(exception):
    users_api_logger.info(exception)
    return make_response(jsonify({'message': exception.message}), exception.code)

@users_api_bp.route('/ping', methods=['GET'])
def ping():
    users_api_logger.info(f"[{datetime.now()}]: Ping Users API") 
    return make_response(jsonify({'message': 'Ping Users API ok'}), 200)

@users_api_bp.route("/users", methods=['POST'])
def register():
    users_api_logger.info(f"[{datetime.now()}]: Register User")
    try: 
        create_user(request)
        return make_response(jsonify({'message': 'user created'}), 201)
    except Exception as ex:
        users_api_logger.error(f"[{datetime.now()}]: Exception -> {ex}") 
        abort(500)

@users_api_bp.route('/users/user/<int:id>', methods=['GET'])
def read_user(id):
    users_api_logger.info(f"[{datetime.now()}]: Get User {id}") 
    user = get_user(id)
    return make_response(jsonify({'user': user.json()}), 200)


@users_api_bp.route('/users/user/<int:id>', methods=['PUT', 'POST'])
def update_user(id):
    users_api_logger.info(f"[{datetime.now()}]: Update User {id}") 
    try:
        update_user(id=id, request=request.form)
    except Exception as ex:
        users_api_logger.error(f"[{datetime.now()}]: Exception -> {ex}") 
        abort(500)

@users_api_bp.route('/users/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    users_api_logger.info(f"[{datetime.now()}]: Delete User {id}") 
    try:
        delete_user(id)
        return make_response(jsonify({'message': 'user deleted'}), 200)
    except Exception as ex:
        users_api_logger.error(f"[{datetime.now()}]: Exception -> {ex}") 
        abort(500)
from flask import request, jsonify, make_response
from . import users_api_bp, users_api_logger, UserIntegrityException, UserNotFound, UnknownException
from datetime import datetime
from .service import create_user, get_user_by_id, update_user, delete_user
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import RegistrationForm

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

@users_api_bp.route("", methods=['POST'])
def create():
    users_api_logger.info(f"[{datetime.now()}]: Register User")
    registration_form = RegistrationForm(request.form)
    if not registration_form.validate():
        errors = {"errors": []}
        for field, messages in registration_form.errors.items():
            for error in messages:
                errors["errors"].append({"field": field, "message": error})
        return jsonify(errors), 400
    
    user = create_user(request.form)
    return make_response(jsonify({'user_data': user }), 201)

@users_api_bp.route('/user/<string:id>', methods=['GET'])
@jwt_required()
def get(id):
    users_api_logger.info(f"[{datetime.now()}]: Get User {id}")
    user_id = get_jwt_identity()
    if id != user_id:
        return make_response(jsonify({'Unauthorized': 'Cannot retrieve data from another user'}), 401)
    if get_user_by_id(user_id) is None:
        return make_response(jsonify({'Unauthorized': 'Invalid user'}), 401)
    user = get_user_by_id(id)
    return make_response(jsonify({'user': user.json()}), 200)

@users_api_bp.route('/user/<string:id>', methods=['PUT', 'POST'])
@jwt_required()
def update(id):
    users_api_logger.info(f"[{datetime.now()}]: Update User {id}")
    if request.form is None:
        return make_response(jsonify({'message': 'No User data provided'}), 400)
    user_id = get_jwt_identity()
    if id != user_id:
        return make_response(jsonify({'Unauthorized': 'Cannot update data from another user'}), 401)
    if get_user_by_id(user_id) is None:
        return make_response(jsonify({'Unauthorized': 'Invalid user'}), 401)
    user = update_user(id, request.form)
    return make_response(jsonify({'user_data': user}), 200)

@users_api_bp.route('/user/<string:id>', methods=['DELETE'])
@jwt_required()
def delete(id):
    users_api_logger.info(f"[{datetime.now()}]: Delete User {id}")
    user_id = get_jwt_identity()
    if id != jwt_id:
        return make_response(jsonify({'Unauthorized': 'Cannot update data from another user'}), 401)
    if get_user_by_id(user_id) is None:
        return make_response(jsonify({'Unauthorized': 'Invalid user'}), 401)
    delete_user(id)
    return make_response(jsonify({'message': 'user deleted'}), 200)

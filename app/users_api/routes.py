from flask import request, jsonify, make_response
from .. import jwt
from . import users_api_bp, users_api_logger, UserIntegrityException, UserNotFound, UnknownException
from datetime import datetime
from .service import create_user, get_user_by_email, update_user_by_email, delete_user_by_email
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import RegistrationForm
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

@users_api_bp.route('/user/<string:email>', methods=['GET'])
@jwt_required()
def get(email):
    users_api_logger.info(f"[{datetime.now()}]: Get User {email}")
    jwt_email = get_jwt_identity()
    if email != jwt_email:
        return make_response(jsonify({'Unauthorized': 'Cannot retrieve data from another user'}), 401)
    user = get_user_by_email(email)
    return make_response(jsonify({'user': user.json()}), 200)

@users_api_bp.route('/user/<string:email>', methods=['PUT', 'POST'])
@jwt_required()
def update(email):
    users_api_logger.info(f"[{datetime.now()}]: Update User {id}")
    if request.form is None:
        return make_response(jsonify({'message': 'No User data provided'}), 400)
    jwt_email = get_jwt_identity()
    if email != jwt_email:
        return make_response(jsonify({'Unauthorized': 'Cannot update data from another user'}), 401)
    user = update_user_by_email(email, request.form)
    return make_response(jsonify({'user_data': user}), 200)

@users_api_bp.route('/user/<string:email>', methods=['DELETE'])
@jwt_required()
def delete(email):
    users_api_logger.info(f"[{datetime.now()}]: Delete User {email}")
    jwt_email = get_jwt_identity()
    if email != jwt_email:
        return make_response(jsonify({'Unauthorized': 'Cannot update data from another user'}), 401)
    delete_user_by_email(email)
    return make_response(jsonify({'message': 'user deleted'}), 200)

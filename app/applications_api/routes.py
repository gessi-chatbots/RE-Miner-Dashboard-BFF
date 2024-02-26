from . import applications_api_bp, applications_api_logger
from flask import request, make_response, jsonify
import json
from datetime import datetime
from .service import (process_applications, 
                      is_application_from_user, 
                      get_all_user_applications)
from ..users_api.service import get_user_by_id
from flask_jwt_extended import jwt_required, get_jwt_identity
responses = {
    'ping': {'message': 'Ping Applications API'},
    'user_id_missing': {'error': 'User ID is missing'},
    'create_applications_success': {'message': 'Create Applications request received successfully'},
    'empty_applications_body': {'message': 'No applications present in request'},
}

@applications_api_bp.route('/ping', methods=['POST'])
def ping():
    applications_api_logger.info(f"[{datetime.now()}]: Ping Applications API")
    return make_response(jsonify(responses['ping']), 200)


@applications_api_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_user_applications():
    applications_api_logger.info(f"[{datetime.now()}]: Get all user applications")
    user_id = get_jwt_identity()
    if get_user_by_id(user_id) is None:
        return make_response(jsonify({'Unauthorized': 'Invalid user'}), 401)
    user_applications = get_all_user_applications(user_id)
    return None

@applications_api_bp.route('/', methods=['POST'])
@jwt_required()
def create_applications():
    applications_api_logger.info(f"[{datetime.now()}]: Create Applications request")
    applications_list = json.loads(json.dumps(request.get_json()))
    if len(applications_list) == 0:
        return make_response(jsonify(responses['empty_applications_body']), 400)
    user_id = get_jwt_identity()
    if get_user_by_id(user_id) is None:
        return make_response(jsonify({'Unauthorized': 'Invalid user'}), 401)
    process_applications(user_id, applications_list)
    return make_response(jsonify(responses['create_applications_success']), 200)
    
@applications_api_bp.route('/application/<string:id>', methods=['PUT', 'POST'])
@jwt_required()
def edit_application(id):
    applications_api_logger.info(f"[{datetime.now()}]: 'Edit Application {id} data")
    user_id = get_jwt_identity()
    if get_user_by_id(user_id) is None:
        return make_response(jsonify({'Unauthorized': 'Invalid user'}), 401)
    if not is_application_from_user(user_id):
        return make_response(jsonify(responses['not_user_application']), 401)
    return make_response(jsonify(responses['edit_application_success']), 200)

@applications_api_bp.route('/application/<string:id>', methods=['DELETE'])
def delete_user_application(id):
    user_id = get_jwt_identity()
    applications_api_logger.info(f"[{datetime.now()}]: Get Application {id} data")
    if not is_application_from_user(user_id):
        return make_response(jsonify(responses['not_user_application']), 401)
    return None

@applications_api_bp.route('/application/<string:id>', methods=['GET'])
def get_user_application(id):
    user_id = get_jwt_identity()
    applications_api_logger.info(f"[{datetime.now()}]: Get Application {id} data")
    if not is_application_from_user(user_id):
        return make_response(jsonify(responses['not_user_application']), 401)
    return None
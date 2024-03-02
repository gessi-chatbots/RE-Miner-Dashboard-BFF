from . import applications_api_bp, applications_api_logger
from flask import request, make_response, jsonify
import json
from datetime import datetime
from app.applications_api.service import (process_applications, 
                                          is_application_from_user, 
                                          get_all_user_applications,
                                          get_application,
                                          edit_application,
                                          delete_application)
from app.users_api.service import get_user_by_id
from flask_jwt_extended import jwt_required, get_jwt_identity

responses = {
    'ping': {'message': 'Ping Applications API'},
    'user_id_missing': {'error': 'User ID is missing'},
    'create_applications_success': {'message': 'Uploaded data to database'},
    'empty_applications_body': {'error': 'No applications present in request'},
    'unauthorized': {'Unauthorized': 'No applications present in request'},
    'edit_application_success': {'message': 'Application updated successfully'},
    'delete_application_success': {'message': 'Application has been deleted successfully'},
    'not_user_application': {'message': 'User does not have assigned the requested application'}
}

@applications_api_bp.route('/ping', methods=['POST'])
def ping():
    applications_api_logger.info(f"[{datetime.now()}]: Ping Applications API")
    return make_response(jsonify(responses['ping']), 200)

# TODO connect to GraphDB to retrieve full data from apps
@applications_api_bp.route('', methods=['GET'])
@jwt_required()
def get_all():
    applications_api_logger.info(f"[{datetime.now()}]: Get all user applications")
    user_id = get_jwt_identity()
    if get_user_by_id(user_id) is None:
        return make_response(jsonify(responses['unauthorized']), 401)
    user_applications = get_all_user_applications(user_id)
    if len(user_applications['applications']) == 0:
        return make_response('no content', 204)
    else:
        return make_response(jsonify(user_applications), 200)
    

# TODO connect to GraphDB to save full data from apps
@applications_api_bp.route('', methods=['POST'])
@jwt_required()
def create_applications():
    applications_api_logger.info(f"[{datetime.now()}]: Create Applications request")
    applications_list = []
    if 'Content-Type' in request.headers and 'application/json' in request.headers['Content-Type']:
        applications_list = request.get_json()
    elif 'applications_file' in request.files:
        applications_file = request.files['applications_file']
        applications_list = json.load(applications_file)
    else:
        return make_response(jsonify({'error': 'Unsupported Media Type'}), 415)

    if len(applications_list) == 0:
        return make_response(jsonify(responses['empty_applications_body']), 400)
    
    user_id = get_jwt_identity()
    if get_user_by_id(user_id) is None:
        return make_response(jsonify(responses['unauthorized']), 401)
    
    applications = process_applications(user_id, applications_list)
    return make_response(jsonify(applications), 201)

# TODO connect to GraphDB to edit data from apps
@applications_api_bp.route('/application/<string:application_id>', methods=['PUT', 'POST'])
@jwt_required()
def update_application(application_id):
    applications_api_logger.info(f"[{datetime.now()}]: 'Edit Application {application_id} data")
    user_id = get_jwt_identity()
    if get_user_by_id(user_id) is None:
        return make_response(jsonify(responses['unauthorized']), 401)
    if not is_application_from_user(application_id, user_id):
        return make_response(jsonify(responses['not_user_application']), 401)
    application_data = request.get_json()
    updated_application = edit_application(application_data)
    return make_response(jsonify(responses['edit_application_success'], updated_application), 200)

@applications_api_bp.route('/application/<string:application_id>', methods=['DELETE'])
@jwt_required()
def delete_user_application(application_id):
    applications_api_logger.info(f"[{datetime.now()}]: 'Delete Application {application_id} data")
    user_id = get_jwt_identity()
    if get_user_by_id(user_id) is None:
        return make_response(jsonify(responses['unauthorized']), 401)
    if not is_application_from_user(application_id, user_id):
        return make_response(jsonify(responses['not_user_application']), 401)
    delete_application(application_id)
    return make_response(jsonify(responses['delete_application_success']), 204)

@applications_api_bp.route('/application/<string:application_id>', methods=['GET'])
@jwt_required()
def get_user_application(application_id):
    applications_api_logger.info(f"[{datetime.now()}]: Get Application {application_id} data")
    user_id = get_jwt_identity()
    if get_user_by_id(user_id) is None:
        return make_response(jsonify(responses['unauthorized']), 401)
    if not is_application_from_user(application_id, user_id):
        return make_response(jsonify(responses['not_user_application']), 401)
    application_data = get_application(application_id)
    return make_response(application_data, 200)
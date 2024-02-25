from . import applications_api_bp, applications_api_logger
from flask import request, make_response, jsonify
import json
from datetime import datetime
from .service import process_applications
from flask_jwt_extended import jwt_required
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

@applications_api_bp.route('/', methods=['POST'])
@jwt_required()
def create_applications():
    applications_api_logger.info(f"[{datetime.now()}]: Create Applications request")
    applications_json = json.loads(request.get_json())
    if applications_json is None:
        return make_response(jsonify(responses['empty_applications_body']), 400)
    
    process_applications(request.get_json())
    return make_response(jsonify(responses['create_applications_success']), 200)
    
@applications_api_bp.route('/application/<string:id>', methods=['PUT', 'POST'])
def edit_application(id):
    applications_api_logger.info(f"[{datetime.now()}]: 'Edit Application {id} data")
    return None

@applications_api_bp.route('/application/<string:id>', methods=['GET'])
def get_application(id):
    applications_api_logger.info(f"[{datetime.now()}]: Get Application {id} data")
    return None


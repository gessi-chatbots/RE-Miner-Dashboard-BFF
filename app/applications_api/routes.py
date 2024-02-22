from . import applications_api_bp, applications_api_logger
from flask import request, make_response, jsonify
import json
from datetime import datetime

responses = {
    'ping': {'message': 'Ping Applications API'},
    'user_id_missing': {'error': 'User ID is missing'},
    'create_applications_success': {'message': 'Create Applications request received successfully'},
    'empty_applications_body': {'message': 'No applications present in request'},
}

@applications_api_bp.get('/ping')
def delete_application():
    applications_api_logger.info(f"[{datetime.now()}]: Ping Applications API")
    return make_response(jsonify(responses['ping']), 200)

@applications_api_bp.post('/')
def create_applications():
    applications_api_logger.info(f"[{datetime.now()}]: Create Applications request")
    user_id = request.args.get('user_id')
    if user_id is None:
        return make_response(jsonify(responses['user_id_missing']), 400)
    applications_json = json.loads(request.get_json())
    if applications_json is None:
        return make_response(jsonify(responses['empty_applications_body']), 400)
    
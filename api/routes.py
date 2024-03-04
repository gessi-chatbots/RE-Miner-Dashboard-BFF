from datetime import datetime
from flask import request, jsonify, make_response, abort, Blueprint
from flask_jwt_extended import (set_access_cookies, 
                                set_refresh_cookies, 
                                jwt_required,
                                get_jwt_identity,
                                unset_jwt_cookies)
import logging
import json
import api.forms as api_forms
import api.utils as api_utils
import api.service.authentication_service as authentication_service
import api.service.user_service as user_service
import api.service.review_service as review_service
import api.service.application_service as application_service
import api.responses as api_responses
import api.exceptions as api_exceptions
# API version
api_name = 'api'
api_version = 'v1'

# API Blueprint
api_bp = Blueprint('api_bp', __name__)

# API Logger configuration
api_logger = logging.getLogger('api')
api_logger.setLevel(logging.DEBUG)
api_logger.addHandler(logging.FileHandler(f'logs/[{datetime.now().date()}]api.log'))

def validate_user(user_id):
    jwt_id = get_jwt_identity()
    if jwt_id != user_id:
        raise api_exceptions.UnauthorizedUserException
    if user_service.get_user_by_id(user_id) is None:
        return api_exceptions.UnauthorizedUserException

@api_bp.errorhandler(api_exceptions.UnauthorizedUserException)
def handle_unauthorized_user(exception):
    api_logger.error(exception)
    return make_response(jsonify({'message': exception.message}), exception.code)

@api_bp.errorhandler(api_exceptions.ApplicationNotFoundException)
def handle_application_not_found(exception):
    api_logger.error(exception)
    return make_response(jsonify({'message': exception.message}), exception.code)

@api_bp.errorhandler(api_exceptions.UserNotFoundException)
def handle_user_not_found(exception):
    api_logger.error(exception)
    return make_response(jsonify({'message': exception.message}), exception.code)

@api_bp.errorhandler(api_exceptions.ReviewNotFoundException)
def handle_review_not_found(exception):
    api_logger.error(exception)
    return make_response(jsonify({'message': exception.message}), exception.code)


@api_bp.errorhandler(api_exceptions.UnknownException)
def handle_user_not_found(exception):
    api_logger.error(exception)
    return make_response(jsonify({'message': exception.message}), exception.code)

@api_bp.errorhandler(api_exceptions.UserIntegrityException)
def handle_integrity_error(exception):
    api_logger.error(exception)
    return make_response(jsonify({'message': exception.message}), exception.code)

@api_bp.route('/ping', methods=['GET'])
def ping():
    api_logger.info(f"[{datetime.now()}]: Ping API") 
    return make_response(jsonify({'message': 'API ok'}), 200)

# -------------- Authentication --------------
@api_bp.route('/login', methods=['POST'])
def login():
    api_logger.info(f"[{datetime.now()}]: Login User")
    login_form = api_forms.LoginForm(request.form)
    api_utils.validate_form(login_form)
    email = login_form.email.data
    password = login_form.password.data
    if not user_service.check_valid_user(email, password):
        abort(401, description='Invalid credentials')
    access_token = authentication_service.generate_access_token(email)
    refresh_token = authentication_service.generate_refresh_token(email)
    resp = jsonify({'login': True})
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp, 200

@api_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    api_logger.info(f"[{datetime.now()}]: Refresh token request") 
    resp = jsonify({'refresh': True})
    id = get_jwt_identity()
    set_access_cookies(resp, authentication_service.refresh_access_token(id))
    return resp, 200

@api_bp.route('/logout', methods=['POST'])
def logout():
    api_logger.info(f"[{datetime.now()}]: Logout") 
    resp = jsonify({'logout': True})
    unset_jwt_cookies(resp)
    return resp, 200

# -------------- User --------------
@api_bp.route("/users", methods=['POST'])
def create_user():
    api_logger.info(f"[{datetime.now()}]: Register User")
    registration_form = api_forms.RegistrationForm(request.form)
    api_utils.validate_form(registration_form)
    user = user_service.create_user(request.form)
    return make_response(jsonify({'user_data': user }), 201)

@api_bp.route('/users/<string:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    api_logger.info(f"[{datetime.now()}]: Get User {user_id}")
    validate_user(user_id)
    user = user_service.get_user_by_id(user_id)
    return make_response(jsonify({'user': user.json()}), 200)

@api_bp.route('/users/<string:user_id>', methods=['PUT', 'POST'])
@jwt_required()
def update_user(user_id):
    api_logger.info(f"[{datetime.now()}]: Update User {user_id}")
    validate_user(user_id)
    if request.form is None:
        return make_response(jsonify({'message': 'No User data provided'}), 400)
    user = user_service.update_user(user_id, request.form)
    return make_response(jsonify({'user_data': user}), 200)

@api_bp.route('/users/<string:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    api_logger.info(f"[{datetime.now()}]: Delete User {id}")
    validate_user(user_id)
    user_service.delete_user(user_id)
    return make_response(jsonify({'message': 'user deleted'}), 200)

# -------------- Applications --------------
@api_bp.route('/users/<string:user_id>/applications', methods=['GET'])
@jwt_required()
def get_applications(user_id):
    api_logger.info(f"[{datetime.now()}]: Get all user {user_id} applications")
    validate_user(user_id)
    user_applications = application_service.get_applications(user_id)
    if len(user_applications['applications']) == 0:
        return make_response('no content', 204)
    else:
        return make_response(jsonify(user_applications), 200)
    
@api_bp.route('/users/<string:user_id>/applications', methods=['POST'])
@jwt_required()
def create_applications(user_id):
    api_logger.info(f"[{datetime.now()}]: Create Applications for user {user_id} request")
    validate_user(user_id)
    applications_list = []
    if 'Content-Type' in request.headers and 'application/json' in request.headers['Content-Type']:
        applications_list = request.get_json()
    elif 'applications_file' in request.files:
        applications_file = request.files['applications_file']
        applications_list = json.load(applications_file)
    else:
        return make_response(jsonify({'error': 'Unsupported Media Type'}), 415)

    if len(applications_list) == 0:
        return make_response(jsonify(api_responses.responses['empty_applications_body']), 400)
    
    applications = application_service.process_applications(user_id, applications_list)
    return make_response(jsonify(applications), 201)

@api_bp.route('/users/<string:user_id>/applications/<string:application_id>', methods=['PUT', 'POST'])
@jwt_required()
def update_application(user_id, application_id):
    api_logger.info(f"[{datetime.now()}]: 'Edit User {user_id} Application {application_id} data")
    validate_user(user_id)
    if not application_service.is_application_from_user(user_id, application_id):
        return make_response(jsonify(api_responses.responses['not_user_application']), 401)
    updated_application = application_service.edit_application(request.get_json())
    return make_response(jsonify(updated_application), 200)

@api_bp.route('/users/<string:user_id>/applications/<string:application_id>', methods=['DELETE'])
@jwt_required()
def delete_application(user_id, application_id):
    api_logger.info(f"[{datetime.now()}]: 'Delete Application {application_id} data")
    validate_user(user_id)
    application_service.delete_application(user_id, application_id)
    return make_response(jsonify(api_responses.responses['delete_application_success']), 204)

@api_bp.route('/users/<string:user_id>/applications/<string:application_id>', methods=['GET'])
@jwt_required()
def get_application(user_id, application_id):
    api_logger.info(f"[{datetime.now()}]: Get Application {application_id} data")
    validate_user(user_id)
    application_data = application_service.get_application(user_id, application_id)
    if application_data is None:
        return make_response(jsonify({'message': 'Application not found for the given user'}), 404)
    return make_response(application_data, 200)

# -------------- Reviews --------------
@api_bp.route('/users/<string:user_id>/applications/<string:application_id>/reviews', methods=['POST'])
@jwt_required()
def create_review(user_id, application_id):
    api_logger.info(f"[{datetime.now()}]: Create Review for User's {user_id} Application {application_id}")
    validate_user(user_id)
    review_form = api_forms.ReviewForm(request.form)
    api_utils.validate_form(review_form)
    review = review_service.create_review(user_id, application_id, review_form.to_dict())
    return make_response(jsonify(review), 201)

@api_bp.route('/users/<string:user_id>/applications/<string:application_id>/reviews', methods=['GET'])
@jwt_required()
def get_all_reviews(user_id, application_id):
    api_logger.info(f"[{datetime.now()}]: Get User {user_id} Application {application_id} Reviews")
    validate_user(user_id)    
    reviews_data = review_service.get_reviews_by_user_application(user_id, application_id)
    if reviews_data is None: 
        return make_response(f'not found any reviews for user {user_id} and {application_id}', 404)
    if len(reviews_data['reviews']) == 0:
        return make_response('no content', 204)
    else:
        return make_response(jsonify(reviews_data), 200)
    
@api_bp.route('/users/<string:user_id>/applications/<string:application_id>/reviews/<string:review_id>', methods=['GET'])
@jwt_required()
def get_review(user_id, application_id, review_id):
    api_logger.info(f"[{datetime.now()}]: Get Review {review_id}")
    validate_user(user_id)
    if not review_service.has_user_review(user_id, application_id, review_id):
        return make_response(jsonify(api_responses.responses['not_user_review']), 401)
    review_data = review_service.get_review(user_id, application_id, review_id)
    return make_response(jsonify(review_data), 200)

@api_bp.route('/users/<string:user_id>/applications/<string:application_id>/reviews/<string:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(user_id, application_id, review_id):
    api_logger.info(f"[{datetime.now()}]: Delete Review {review_id}")
    validate_user(user_id)
    if not review_service.has_user_review(user_id, application_id, review_id):
        return make_response(jsonify(api_responses.responses['not_user_review']), 401)
    review_service.delete_review(user_id, application_id, review_id)
    return make_response(jsonify(api_responses.responses['delete_review_success']), 204)

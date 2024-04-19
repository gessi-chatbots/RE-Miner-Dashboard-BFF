from datetime import datetime
from flask import request, jsonify, make_response, abort, Blueprint, send_file
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

#---------------------------------------------------------------------------
#   API Versioning
#---------------------------------------------------------------------------
api_name = 'api'
api_version = 'v1'

#---------------------------------------------------------------------------
#   API Blueprint
#---------------------------------------------------------------------------
api_bp = Blueprint('api_bp', __name__)

#---------------------------------------------------------------------------
#   API Logging Configuration
#---------------------------------------------------------------------------
api_logger = logging.getLogger('api')
api_logger.setLevel(logging.INFO)
api_logger.addHandler(logging.FileHandler(f'logs/[{datetime.now().date()}]api.log'))

#---------------------------------------------------------------------------
#   Exception Handlers
#---------------------------------------------------------------------------
@api_bp.errorhandler(api_exceptions.UnauthorizedUserException)
def handle_unauthorized_user(exception):
    api_logger.error(exception)
    return make_response(jsonify({'message': exception.message}), exception.code)


@api_bp.errorhandler(api_exceptions.HUBException)
def handle_hub_exception(exception):
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

@api_bp.errorhandler(api_exceptions.KGRException)
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

@api_bp.errorhandler(api_exceptions.KGRConnectionException)
def handle_connection_error(exception):
    api_logger.error(exception)
    return make_response(jsonify({'message': exception.message}), exception.code)

@api_bp.errorhandler(api_exceptions.ReviewNotFromUserException)
def handle_review_not_from_user_error(exception):
    api_logger.error(exception)
    return make_response(jsonify({'message': exception.message}), exception.code)

@api_bp.errorhandler(api_exceptions.KGRApplicationNotFoundException)
def handle_kgr_app_not_found_exception(exception):
    api_logger.error(exception)
    return make_response(jsonify({'message': exception.message}), exception.code)


@api_bp.errorhandler(api_exceptions.KGRApplicationsNotFoundException)
def handle_kgr_apps_not_found_exception(exception):
    api_logger.error(exception)
    return make_response(jsonify({'message': exception.message}), exception.code)

@api_bp.errorhandler(api_exceptions.KGRReviewsNotFoundException)
def handle_kgr_reviews_not_found_exception(exception):
    api_logger.error(exception)
    return make_response(jsonify({'message': exception.message}), exception.code)

#---------------------------------------------------------------------------
#   API health check
#---------------------------------------------------------------------------
@api_bp.route('/ping', methods=['GET'])
def ping():
    api_logger.info(f"[{datetime.now()}]: Ping API") 
    return make_response(jsonify({'message': 'API ok'}), 200)

#---------------------------------------------------------------------------
#   Authentication & User Endpoints
#---------------------------------------------------------------------------
def validate_user(user_id):
    jwt_id = get_jwt_identity()
    if jwt_id is not None and jwt_id != user_id:
        raise api_exceptions.UnauthorizedUserException
    if user_service.get_user_by_id(user_id) is None:
        return api_exceptions.UnauthorizedUserException
    
@api_bp.route('/login', methods=['POST'])
def login():
    api_logger.info(f"[{datetime.now()}]: Login User")
    login_form = api_forms.LoginForm(request.form)
    api_utils.validate_form(login_form)
    email = login_form.email.data
    password = login_form.password.data
    if not user_service.check_valid_user(email, password):
        abort(401, description='Invalid credentials')
    user = user_service.get_user_by_email(email)

    access_token = authentication_service.generate_access_token(email)
    refresh_token = authentication_service.generate_refresh_token(email)
    resp = jsonify({'user_data': user.json(), 
                    'access_token': access_token, 
                    'refresh_token': refresh_token }) 
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token) 
    resp.headers['X-Access-Token'] = access_token
    resp.headers['X-Refresh-Token'] = refresh_token
    return make_response(resp, 200)

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

@api_bp.route("/users", methods=['POST', 'OPTIONS'])
def create_user():
    if request.method == 'OPTIONS':
        # Handle OPTIONS request (preflight)
        headers = {
            'Access-Control-Allow-Origin': 'http://localhost:3000',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
        return ('', 204, headers)
    
    # Actual POST request handling
    api_logger.info(f"[{datetime.now()}]: Register User")
    registration_form = api_forms.RegistrationForm(request.form)
    api_utils.validate_form(registration_form)
    user = user_service.create_user(request.form)
    response = make_response(jsonify({'user_data': user }), 201)
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    return response

@api_bp.route('/users/<string:user_id>', methods=['GET'])
@jwt_required(optional=True)
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
    return make_response(jsonify({'message': 'user deleted'}), 204)

#---------------------------------------------------------------------------
#   Analysis Endpoints
#---------------------------------------------------------------------------
@api_bp.route('/users/<string:user_id>/analyze', methods=['POST'])
@jwt_required(optional=True)
def analyze_reviews(user_id):
    api_logger.info(f"[{datetime.now()}]: Analyze User {user_id} Reviews")
    if not request.args \
            or ('sentiment_model' not in request.args.keys() and 'feature_model' not in request.args.keys()):
                return "Lacking model and textual data in proper tag.", 400
    feature_model = request.args.get('feature_model')
    sentiment_model = request.args.get('sentiment_model')
    validate_user(user_id)
    if request.json is None:
        return make_response(jsonify({'message': 'no body'}), 406)
    reviews = request.json
    analyzed_reviews = review_service.analyze_reviews(user_id, reviews, feature_model, sentiment_model)
    return make_response(jsonify(analyzed_reviews), 200)

@api_bp.route('/performance/analyze', methods=['POST'])
@jwt_required()
def test_analyisis_performance():
    if request.json is None:
        return make_response(jsonify({'message': 'no body'}), 406)
    reviews = request.json
    review_service.test_performance(reviews)
    return make_response(jsonify({'message': 'ok'}), 200)

@api_bp.route('/users/<string:user_id>/analyze/top-sentiments', methods=['POST'])
@jwt_required(optional=True)
def topUserSentimentsByAppNames(user_id):
    api_logger.info(f"[{datetime.now()}]: Get User {user_id} top sentiments")
    validate_user(user_id)
    if request.json is None:
        return make_response(jsonify({'message': 'no body'}), 406)
    app_names = request.json.get('data')
    top_sentiments = application_service.get_top_sentiments(user_id, app_names)
    return make_response(jsonify(top_sentiments), 200)


@api_bp.route('/users/<string:user_id>/analyze/top-features', methods=['POST'])
@jwt_required(optional=True)
def topUserFeaturesByAppNames(user_id):
    api_logger.info(f"[{datetime.now()}]: Get User {user_id} top sentiments")
    validate_user(user_id)
    if request.json is None:
        return make_response(jsonify({'message': 'no body'}), 406)
    app_names = request.json.get('data')
    top_features = application_service.get_top_features(user_id, app_names)
    return make_response(jsonify(top_features), 200)

@api_bp.route('/users/<string:user_id>/applications/<string:app_id>/statistics', methods=['GET'])
@jwt_required(optional=True)
def statistics(user_id, app_id):
    api_logger.info(f"[{datetime.now()}]: Get User {user_id} statistics")
    validate_user(user_id)
    if not request.args or ('start_date' not in request.args and 'end_date' not in request.args):
        return make_response(jsonify({'message': 'start_date or end_date parameter is missing'}), 400)

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    statistics = application_service.get_app_statistics(app_id, start_date, end_date)
    return make_response(jsonify(statistics), 200)

#---------------------------------------------------------------------------
#   Application Endpoints
#---------------------------------------------------------------------------
@api_bp.route('/applications/directory', methods=['GET'])
@jwt_required(optional=True)
def get_applications_from_directory():
    api_logger.info(f"[{datetime.now()}]: Get all Applications from directory request")
    directory_applications = application_service.get_applications_from_directory()
    if len(directory_applications) == 0:
        return make_response('no content', 204)
    else:
        return make_response(directory_applications, 200)

@api_bp.route('/applications/directory', methods=['POST'])
@jwt_required(optional=True)
def add_application_data_from_directory():
    api_logger.info(f"[{datetime.now()}]: Add applications from directory data request") 
    if 'user_id' not in request.args:
        return make_response({"message": "no user id was specified"}, 400)
    user_id = request.args.get('user_id')
    applications_list = []
    if 'Content-Type' in request.headers and 'application/json' in request.headers['Content-Type']:
        applications_list = request.get_json()
        if not isinstance(applications_list, list): 
            return make_response({"message": "You must specify a list"}, 400)
        if len(applications_list) == 0:
            return make_response({"message": "no application list specified in body"}, 400)
    app = application_service.add_applications_from_directory_to_user(user_id, applications_list)
    return make_response(app, 200)

@api_bp.route('/applications/directory/<string:app_name>', methods=['GET'])
@jwt_required()
def get_application_data_from_directory(app_name):
    api_logger.info(f"[{datetime.now()}]: Get Application {app_name} directory data request")
    directory_application = application_service.get_application_from_directory(app_name)
    return make_response(jsonify(directory_application), 200)

@api_bp.route('/users/<string:user_id>/applications', methods=['GET'])
@jwt_required(optional=True)
def get_applications(user_id):
    api_logger.info(f"[{datetime.now()}]: Get all user {user_id} applications")
    validate_user(user_id)
    page = request.args.get('page', default=1, type=int)
    page_size = request.args.get('pageSize', default=8, type=int)
    user_applications, total_pages = application_service.get_applications(user_id, page, page_size)
    if not user_applications:
        return make_response('no content', 204)
    else:
        response_data = {
            "applications": user_applications,
            "total_pages": total_pages
        }
        return make_response(jsonify(response_data), 200)

@api_bp.route('/users/<string:user_id>/applications', methods=['POST'])
@jwt_required(optional=True)
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
@jwt_required(optional=True)
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


@api_bp.route('/users/<string:user_id>/applications/<string:application_id>/features', methods=['GET'])
@jwt_required(optional=True)
def get_application_features(user_id, application_id):
    api_logger.info(f"[{datetime.now()}]: Get Application {application_id} data")
    validate_user(user_id)
    features = application_service.get_application_features(application_id)
    return make_response(features, 200)

#---------------------------------------------------------------------------
#   Review Endpoints
#---------------------------------------------------------------------------
@api_bp.route('/users/<string:user_id>/applications/<string:application_id>/reviews', methods=['POST'])
@jwt_required()
def create_review(user_id, application_id):
    api_logger.info(f"[{datetime.now()}]: Create Review for User's {user_id} Application {application_id}")
    validate_user(user_id)
    review_form = api_forms.ReviewForm(request.form)
    api_utils.validate_form(review_form)
    review = review_service.create_review(user_id, application_id, review_form.to_dict())
    return make_response(jsonify(review), 201)

@api_bp.route('/users/<string:user_id>/reviews', methods=['GET'])
@jwt_required(optional=True)
def get_all_user_reviews(user_id):
    api_logger.info(f"[{datetime.now()}]: Get User {user_id} reviews")
    page = request.args.get('page', type=int)
    page_size = request.args.get('pageSize', type=int)
    reviews_data = review_service.get_reviews_by_user(user_id, page, page_size)
    if reviews_data['reviews']:
        return make_response(jsonify(reviews_data), 200)
    elif reviews_data['total_pages'] == 0:
        return make_response('no content', 204)
    else:
        return make_response(f'no reviews found for page {page}', 204)


@api_bp.route('/users/<string:user_id>/applications/<string:application_id>/reviews', methods=['GET'])
@jwt_required()
def get_all_user_application_reviews(user_id, application_id):
    api_logger.info(f"[{datetime.now()}]: Get User {user_id} Application {application_id} Reviews")
    validate_user(user_id)  
    reviews_data = review_service.get_reviews_by_user_application(user_id, application_id)
    if reviews_data is None:
        return make_response(f'not found any reviews for user {user_id} and {application_id}', 404)
    if len(reviews_data) == 0:
        return make_response('no content', 204)
    else:
        return make_response(jsonify(reviews_data), 200)
    
@api_bp.route('/users/<string:user_id>/applications/<string:application_id>/reviews/<string:review_id>', methods=['GET'])
@jwt_required(optional=True)
def get_review(user_id, application_id, review_id):
    api_logger.info(f"[{datetime.now()}]: Get Review {review_id}")
    validate_user(user_id)
    review_data = review_service.get_review(user_id, application_id, review_id)
    return make_response(review_data, 200)

@api_bp.route('/users/<string:user_id>/applications/<string:application_id>/reviews/<string:review_id>', methods=['DELETE'])
@jwt_required(optional=True)
def delete_review(user_id, application_id, review_id):
    api_logger.info(f"[{datetime.now()}]: Delete Review {review_id}")
    validate_user(user_id)
    review_service.delete_review(user_id, application_id, review_id)
    return make_response(jsonify(api_responses.responses['delete_review_success']), 204)

@api_bp.route('/users/<string:user_id>/applications/<string:application_id>/reviews/<string:review_id>/analyze', methods=['POST'])
@jwt_required(optional=True)
def analyze_review(user_id, application_id, review_id):
    api_logger.info(f"[{datetime.now()}]: Analyze Review {review_id} for User's {user_id} Application {application_id}")
    validate_user(user_id)
    analyze_form = api_forms.AnalyzeForm(request.form)
    api_utils.validate_form(analyze_form)
    review = review_service.analyze_review(user_id, application_id, review_id)
    return make_response(jsonify(review), 201)

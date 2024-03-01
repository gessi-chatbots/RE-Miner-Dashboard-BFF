from . import reviews_api_bp, reviews_api_logger
from flask import make_response, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import app.users_api.service as users_api_service
import app.reviews_api.service as reviews_api_service
import app.reviews_api.forms as reviews_api_forms
from datetime import datetime

responses = {
    'ping': {'message': 'Ping Reviews API'},
    'user_id_missing': {'error': 'User ID is missing'},
    'create_reviews_success': {'message': 'Uploaded reviews to database'},
    'empty_reviews_body': {'error': 'No reviews present in request'},
    'unauthorized': {'Unauthorized': 'Not a valid user'},
    'update_review_success': {'message': 'Review updated successfully'},
    'delete_review_success': {'message': 'Review has been deleted successfully'},
    'not_user_review': {'message': 'User does not have assigned the requested review'}
}

@reviews_api_bp.route('/ping', methods=['GET'])
def ping():
    reviews_api_logger.info(f"[{datetime.now()}]: Ping Reviews API")
    return make_response(jsonify(responses['ping']), 200)

@reviews_api_bp.route('/<string:application_name>', methods=['POST'])
@jwt_required()
def create_review(application_name):
    reviews_api_logger.info(f"[{datetime.now()}]: Create Review for application {application_name}")
    user_id = get_jwt_identity()
    if users_api_service.get_user_by_id(user_id) is None:
        return make_response(jsonify(responses['unauthorized']), 401)
    review_form = reviews_api_forms.ReviewForm(request.form)
    if not review_form.validate():
        errors = {"errors": []}
        for field, messages in review_form.errors.items():
            for error in messages:
                errors["errors"].append({"field": field, "message": error})
        return jsonify(errors), 400
    if application_name is None: 
        return make_response('no application name in query params', 400)
    reviews_api_service.process_review(user_id, application_name, review_form.to_dict(), commit=True)
    return make_response(jsonify({"message":"created"}), 201)

@reviews_api_bp.route('', methods=['GET'])
@jwt_required()
def get_all():
    reviews_api_logger.info(f"[{datetime.now()}]: Get User Reviews")
    user_id = get_jwt_identity()
    if users_api_service.get_user_by_id(user_id) is None:
        return make_response(jsonify(responses['unauthorized']), 401)
    reviews_data = reviews_api_service.get_all_reviews_from_user(user_id)
    if len(reviews_data['reviews']) == 0:
        return make_response('no content', 204)
    else:
        return make_response(jsonify(reviews_data), 200)
    

@reviews_api_bp.route('/review/<string:review_id>', methods=['GET'])
@jwt_required()
def get(review_id):
    reviews_api_logger.info(f"[{datetime.now()}]: Get Review {review_id}")
    user_id = get_jwt_identity()
    if users_api_service.get_user_by_id(user_id) is None:
        return make_response(jsonify(responses['unauthorized']), 401)
    if not reviews_api_service.is_review_from_user(review_id, user_id):
        return make_response(jsonify(responses['not_user_review']), 401)
    review_data = reviews_api_service.get_review_data(review_id)
    return make_response(jsonify(review_data), 200)

@reviews_api_bp.route('/review/<string:review_id>', methods=['DELETE'])
@jwt_required()
def delete(review_id):
    reviews_api_logger.info(f"[{datetime.now()}]: Delete Review {review_id}")
    user_id = get_jwt_identity()
    if users_api_service.get_user_by_id(user_id) is None:
        return make_response(jsonify(responses['unauthorized']), 401)
    if not reviews_api_service.is_review_from_user(review_id, user_id):
        return make_response(jsonify(responses['not_user_review']), 401)
    reviews_api_service.delete_review(review_id)
    return make_response(jsonify(responses['delete_review_success']), 204)

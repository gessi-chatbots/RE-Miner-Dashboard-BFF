from . import reviews_api_bp, reviews_api_logger
from flask import make_response, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.users_api.service import get_user_by_id
from app.reviews_api.service import process_review, is_review_from_user
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

@reviews_api_bp.route('/', methods=['POST'])
@jwt_required()
def create_review():
    reviews_api_logger.info(f"[{datetime.now()}]: Create Review")
    user_id = get_jwt_identity()
    if get_user_by_id(user_id) is None:
        return make_response(jsonify(responses['unauthorized']), 401)
    review_data = request.get_json()
    if review_data is None: 
        return make_response(jsonify(responses['empty_reviews_body']), 400)
    process_review(user_id, review_data, commit=True)

    return make_response(jsonify({"message":"created"}), 201)

@reviews_api_bp.route('/', methods=['GET'])
@jwt_required()
def get_all():
    reviews_api_logger.info(f"[{datetime.now()}]: Get User Reviews")
    user_id = get_jwt_identity()
    if get_user_by_id(user_id) is None:
        return make_response(jsonify(responses['unauthorized']), 401)
    review_data = request.get_json()
    if review_data is None: 
        return make_response(jsonify(responses['empty_reviews_body']), 400)
    updated_review = update_review(review_data)
    return make_response(jsonify(responses['update_review_success'], updated_review), 200)

@reviews_api_bp.route('/review/<string:review_id>', methods=['PUT', 'POST'])
@jwt_required()
def update_review(review_id):
    reviews_api_logger.info(f"[{datetime.now()}]: Update Review {review_id}")
    user_id = get_jwt_identity()
    if get_user_by_id(user_id) is None:
        return make_response(jsonify(responses['unauthorized']), 401)
    if not is_review_from_user(review_id, user_id):
        return make_response(jsonify(responses['not_user_review']), 401)
    return make_response(jsonify({"message":"ok"}), 201)

@reviews_api_bp.route('/review/<string:review_id>', methods=['GET'])
@jwt_required()
def get_review(review_id):
    reviews_api_logger.info(f"[{datetime.now()}]: Get Review {review_id}")
    user_id = get_jwt_identity()
    if get_user_by_id(user_id) is None:
        return make_response(jsonify(responses['unauthorized']), 401)
    if not is_review_from_user(review_id, user_id):
        return make_response(jsonify(responses['not_user_review']), 401)
    review_data = get_review(review_id)
    return make_response(review_data, 200)

@reviews_api_bp.route('/review/<string:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    reviews_api_logger.info(f"[{datetime.now()}]: Delete Review {review_id}")
    user_id = get_jwt_identity()
    if get_user_by_id(user_id) is None:
        return make_response(jsonify(responses['unauthorized']), 401)
    if not is_review_from_user(review_id, user_id):
        return make_response(jsonify(responses['not_user_review']), 401)
    delete_review(review_id)
    return make_response(jsonify(responses['delete_review_success']), 204)

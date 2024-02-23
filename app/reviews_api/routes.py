from . import reviews_api_bp, reviews_api_logger
from flask import make_response, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime

@reviews_api_bp.route('/ping', methods=['GET'])
def ping():
    reviews_api_logger.info(f"[{datetime.now()}]: Ping Reviews API")
    return make_response(jsonify({'message': 'Ping Reviews API ok'}), 200)

@reviews_api_bp.route('/', methods=['POST'])
@jwt_required()
def create_reviews():
    reviews_api_logger.info(f"[{datetime.now()}]: Create Reviews")
    return None

@reviews_api_bp.route('/', methods=['GET'])
@jwt_required()
def get_reviews():
    reviews_api_logger.info(f"[{datetime.now()}]: Get Reviews")
    return None

@reviews_api_bp.route('/review/<string:id>', methods=['PUT', 'POST'])
@jwt_required()
def update_review(id):
    reviews_api_logger.info(f"[{datetime.now()}]: Update Review {id}")
    return None

@reviews_api_bp.route('/review/<string:id>', methods=['GET'])
@jwt_required()
def get_review(id):
    reviews_api_logger.info(f"[{datetime.now()}]: Get Review {id}")
    return None

@reviews_api_bp.route('/review/<string:id>', methods=['DELETE'])
@jwt_required()
def delete_review(id):
    reviews_api_logger.info(f"[{datetime.now()}]: Delete Review {id}")
    return None
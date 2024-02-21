from . import reviews_api_bp, reviews_api_logger
from flask import make_response, jsonify
from datetime import datetime


@reviews_api_bp.get('/ping')
def ping():
    reviews_api_logger.info(f"[{datetime.now()}]: Ping Reviews API")
    return make_response(jsonify({'message': 'Ping Reviews API ok'}), 200)


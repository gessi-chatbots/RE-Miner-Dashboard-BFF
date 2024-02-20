from flask import request, jsonify, make_response
from . import users_api_bp, users_api_logger
from .models import User, db
from datetime import datetime


@users_api_bp.route('/ping', methods=['GET'])
def ping():
    users_api_logger.info(f"[{datetime.now()}]: Ping API Users") 
    return make_response(jsonify({'message': 'ping users api ok'}), 200)

@users_api_bp.post("/users")
def register():
    users_api_logger.info(f"[{datetime.now()}]: Register User") 
    try: 
        name = request.form.get('name')
        family_name = request.form.get('family_name')
        email = request.form.get('email')
        new_user = User(name=name, 
                        family_name=family_name, 
                        email=email) 
        db.session.add(new_user)
        db.session.commit()
        return make_response(jsonify({'message': 'user created'}), 201)
    except: 
        return make_response(jsonify({'message': 'error creating user'}), 500)

@users_api_bp.get('/users/<int:id>')
def get_user(id):
    users_api_logger.info(f"[{datetime.now()}]: Get User {id}") 
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            return make_response(jsonify({'user': user.json()}), 200)
        return make_response(jsonify({'message': 'user not found'}), 404)
    except:
        return make_response(jsonify({'message': 'error getting user'}), 500)

@users_api_bp.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    users_api_logger.info(f"[{datetime.now()}]: Update User {id}") 
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            user.name = request.form.get('name')
            user.family_name = request.form.get('family_name')
            db.session.commit()
            return make_response(jsonify({'message': 'user updated'}), 200)
        return make_response(jsonify({'message': 'user not found'}), 404)
    except:
        return make_response(jsonify({'message': 'error updating user'}), 500)

@users_api_bp.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    users_api_logger.info(f"[{datetime.now()}]: Delete User {id}") 
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return make_response(jsonify({'message': 'user deleted'}), 200)
        return make_response(jsonify({'message': 'user not found'}), 404)
    except:
        return make_response(jsonify({'message': 'error deleting user'}), 500)
from flask import abort, current_app
from . import users_api_logger, UserNotFound
from .models import User, db

def create_user(request):
    name = request.form.get('name')
    family_name = request.form.get('family_name')
    email = request.form.get('email')

    with current_app.app_context():
        new_user = User(name=name, family_name=family_name, email=email) 
        db.session.add(new_user)
        db.session.commit()

def get_user(id):
    user = User.query.get(id)
    if user is None: 
        raise UserNotFound()
    return user

def update_user(id, form):
    user = User.query.get(id)
    if user is None:
        raise UserNotFound

    user.name = form.get('name')
    user.family_name = form.get('family_name')
    db.session.commit()

def delete_user(id):
    user = User.query.get(id)
    if user is None:
        abort(404)
    
    with current_app.app_context():
        db.session.delete(user)
        db.session.commit()

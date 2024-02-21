from flask import current_app
from . import UserNotFound, UserIntegrityException
from .models import User, db
import uuid
from sqlalchemy.exc import IntegrityError

def create_user(request):
    try:
        user_data = {
            'id': str(uuid.uuid4()),
            'name': request.form.get('name'),
            'family_name': request.form.get('family_name'),
            'email': request.form.get('email'),
        }
        new_user = User(**user_data)
        db.session.add(new_user)
        db.session.commit()
        return user_data
    except IntegrityError as e:
        db.session.rollback()
        raise UserIntegrityException

def get_user(id):
    user = User.query.get(id)
    if user is None: 
        raise UserNotFound()
    return user

def update_user(id, form):
    user = User.query.get(id)
    if user is None:
        raise UserNotFound
    try:
        user.name = form.get('name', user.name)
        user.family_name = form.get('family_name', user.family_name)
        db.session.commit()
        return user
    except Exception as e:
        db.session.rollback()


def delete_user(id):
    user = User.query.get(id)
    if user is None:
        raise UserNotFound
    try:
        db.session.delete(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()

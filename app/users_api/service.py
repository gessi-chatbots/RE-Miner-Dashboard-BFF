from . import UserNotFound, UserIntegrityException
from .models import User, db
import uuid
from sqlalchemy.exc import IntegrityError

def create_user(form):
    try:
        user_data = {
            'id': str(uuid.uuid4()),
            'name': form.get('name'),
            'family_name': form.get('family_name'),
            'email': form.get('email'),
            'password': form.get('password')  # Assuming 'password' is in the form data
        }
        new_user = User(**user_data)
        new_user.password = user_data['password']
        db.session.add(new_user)
        db.session.commit()
        return new_user.json()
    except IntegrityError as e:
        db.session.rollback()
        raise UserIntegrityException

def get_user(id):
    user = User.query.get(id)
    if user is None: 
        raise UserNotFound()
    return user.json()

def update_user(id, form):
    user = User.query.get(id)
    if user is None:
        raise UserNotFound
    try:
        user.name = form.get('name', user.name)
        user.family_name = form.get('family_name', user.family_name)
        db.session.commit()
        return user.json()
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

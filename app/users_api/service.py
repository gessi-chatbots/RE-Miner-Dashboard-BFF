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
            'password_hash': form.get('password')
        }
        new_user = User(**user_data)
        db.session.add(new_user)
        db.session.commit()
        return new_user.json()
    except IntegrityError as e:
        db.session.rollback()
        raise UserIntegrityException

def get_user_by_id(id):
    user = User.query.filter_by(id=id).one_or_none()
    if user is None: 
        raise UserNotFound()
    return user

def get_user_by_email(email):
    user = User.query.filter_by(email=email).one_or_none()
    if user is None: 
        raise UserNotFound()
    return user

def update_user_by_email(email, form):
    user = get_user_by_email(email)
    try:
        user.name = form.get('name', user.name)
        user.family_name = form.get('family_name', user.family_name)
        db.session.commit()
        return user.json()
    except Exception as e:
        db.session.rollback()

def delete_user_by_email(email):
    user = get_user_by_email(email)
    try:
        db.session.delete(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()

def check_valid_user(email, password):
    print(email)
    print(password)
    try:
        user = User.query.filter(User.email == email, User.password_hash == password).one()
        return user is not None
    except Exception as e:
        db.session.rollback()
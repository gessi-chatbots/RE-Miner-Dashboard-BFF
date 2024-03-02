import app.api.models as api_models
import app.api.exceptions as api_exceptions
import uuid
from app import db
from sqlalchemy.exc import IntegrityError

def check_valid_user(email, password):
    user = api_models.User.query.filter(api_models.User.email == email, 
                                        api_models.User.password_hash == password).one_or_none()
    return user is not None

def create_user(form):
    try:
        user_data = {
            'id': str(uuid.uuid4()),
            'name': form.get('name'),
            'family_name': form.get('family_name'),
            'email': form.get('email'),
            'password_hash': form.get('password')
        }
        new_user = api_models.User(**user_data)
        db.session.add(new_user)
        db.session.commit()
        return new_user.json()
    except IntegrityError as e:
        db.session.rollback()
        raise api_exceptions.UserIntegrityException

def get_user_by_id(id):
    user = api_models.User.query.filter_by(id=id).one_or_none()
    return user

def get_user_by_email(email):
    user = api_models.User.query.filter_by(email=email).one_or_none()
    return user

def update_user(id, form):
    user = get_user_by_id(id)
    try:
        user.name = form.get('name', user.name)
        user.family_name = form.get('family_name', user.family_name)
        db.session.commit()
        return user.json()
    except Exception as e:
        db.session.rollback()

def delete_user(id):
    user = get_user_by_id(id)
    try:
        db.session.delete(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()

def check_valid_user(email, password):
    user = api_models.User.query.filter(api_models.User.email == email, api_models.User.password_hash == password).one_or_none()
    return user is not None
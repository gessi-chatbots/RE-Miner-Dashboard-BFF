from flask_jwt_extended import create_access_token, create_refresh_token
import app.users_api.service as users_api_service

def generate_access_token(user_email):
    user = users_api_service.get_user_by_email(user_email)
    return create_access_token(identity=user.id)

def generate_refresh_token(user_email):
    user = users_api_service.get_user_by_email(user_email)
    return create_refresh_token(identity=user.id)

def refresh_access_token(user_id):
    user = users_api_service.get_user_by_id(user_id)
    return generate_access_token(user.email)

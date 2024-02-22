from flask_jwt_extended import create_access_token, create_refresh_token

def generate_access_token(email):
    return create_access_token(identity=email)

def generate_refresh_token(email):
    return create_refresh_token(identity=email)
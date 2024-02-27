from flask_jwt_extended import create_access_token, create_refresh_token

def generate_access_token(id):
    return create_access_token(identity=id)

def generate_refresh_token(id):
    return create_refresh_token(identity=id)
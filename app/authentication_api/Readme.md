# Authentication API Documentation

## Introduction

The Authentication API is a user session management module designed to enhance the security of your Flask project. This module efficiently manages user login, access token and refresh token handling, logout, and access token refresh functionalities. By integrating this module into your project, you can establish a robust layer of protection for your API endpoints.

## Design

The API consists of the following files:

- [Initialization file](__init__.py): This file allows basic configuration of the module, such as setting up the blueprint name and configuring logging.

- [API endpoints](routes.py): This file contains the endpoints responsible for managing user sessions and token handling.

- [Service](service.py): Here, you can find business logic, including methods that generate access and refresh tokens.

## How to Install

1. Install the [**Flask JWT Extended**](https://flask-jwt-extended.readthedocs.io/) library:
   - If using a basic `requirements.txt`:
     ```bash
     pip install flask_jwt_extended
     pip freeze > requirements.txt
     ```
   - If using pipenv (highly recommended):
     ```bash
     pipenv install flask_jwt_extended
     ```

2. In your [Flask application set up code](../__init__.py), add the following:
   1. Import library: 
    ```python
        import secrets
        from flask_jwt_extended import JWTManager
    ```
   2. Set up library config: 
    ```python
        # Set JWT cookie to be secure (only sent over HTTPS)
        app.config["JWT_COOKIE_SECURE"] = True

        # Define the location where JWT tokens can be stored
        app.config["JWT_TOKEN_LOCATION"] = ["cookies"]

        # Set the expiration time for access tokens to 1 hour (you can change)
        app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

        # Set the path for the access token cookie based on the general API version 
        # The requests sent to the routes included in this path will contain the access token
        app.config['JWT_ACCESS_COOKIE_PATH'] = f'/api/{general_api_version}'

        # Set the expiration time for refresh tokens to 30 days
        app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

        # Set the path for the refresh token cookie based on the general API version 
        # Here as we only need the refresh token for refreshing the access token, 
        # we limit it to the refresh endpoint. (by doing that, we reduce the cookie qty in the request)
        app.config['JWT_REFRESH_COOKIE_PATH'] = f'/api/{general_api_version}/refresh'

        # Disable CSRF protection for JWT cookies
        app.config['JWT_COOKIE_CSRF_PROTECT'] = False

        # Set a random secret key for encoding and decoding JWT tokens
        app.config["JWT_SECRET_KEY"] = secrets.token_hex(16)

        # Initialize JWTManager with the Flask app
        jwt = JWTManager(app)
    ```
    3. In your [Flask application set up code](../__init__.py), register the Authentication API in your Flask application
    ```python
        # Import the blueprint from the authentication api
        from app.authentication_api.routes import authentication_api_bp

        # Register blueprint in the app and add the desired url prefix
        app.register_blueprint(authentication_api_bp, url_prefix=f'/api/{general_api_version}')
    ```
    
## How to Use It

**IMPORTANT**: It is highly recommended to manage users via a database when using this API. Failure to do so may result in an inability to validate the content within the JWT, potentially leading to security issues. In this section, it is assumed that you have a User Management System.

Once you have properly installed the Authentication API and ensured the correct functioning of the Flask application, you can start using it.

1. Define the content from your user that you want to set in the JWT and establish how to load that user from the database for validation purposes. 
In the following example, we assume the usage of [Users with an ID](../users_api/models.py).

   ```python
        # Load the user ID (for privacy purposes) into the JWT
        @jwt.user_identity_loader
        def user_identity_lookup(user):
            return user.id
    ```
2. For protecting the endpoints you should do as it is done in [this endpoint example from an User API route](../users_api/routes.py):
    ```python
        from flask_jwt_extended import jwt_required, get_jwt_identity
        @users_api_bp.route('/user/<string:id>', methods=['GET'])
        # We specify that JWT is required
        @jwt_required()
        def get(id):
            users_api_logger.info(f"[{datetime.now()}]: Get User {id}")
            # We load the ID that is stored in the JWT
            jwt_id = get_jwt_identity()
            if id != jwt_id:
                return make_response(jsonify({'Unauthorized': 'Cannot retrieve data from another user'}), 401)
            user = get_user_by_id(id)
            return make_response(jsonify({'user': user.json()}), 200)
    ```
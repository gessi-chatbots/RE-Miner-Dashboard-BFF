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
---
**IMPORTANT**: For using this API, user mangament via Database is highly recommended, if not you won't be able to validate what is being sent within the JWT, this can provoke security issues. In this part I am assuming you have an User Management System. 
---
Once you have properly installed the Authentication API and the Flask application runs correctly, you can start using it. 

1. You should define what content from your user you want to set in the JWT and how do you load that user from the database. 
The example that follows represents a situation that we are using [Users and they have an ID](../users_api/models.py), we also use a [service method for retrieving the User](../users_api/service.py).
   ```python
        # We load the user id (privacy purposes) in the JWT
        @jwt.user_identity_loader
        def user_identity_lookup(user):
            return user.id

        # We use a get_user_by_id method from the service layer to retrieve the user 
        # from the ID that comes within the JWT. This allows us to check if it is a 
        # valid user.
        from .service import get_user_by_id
        @jwt.user_lookup_loader
        def user_lookup_callback(_jwt_header, jwt_data):
            return get_user_by_id(jwt_data["sub"])
    ```
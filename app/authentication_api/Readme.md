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

2. In your app setup code, add the following:
   1. Import library: 
    `from flask_jwt_extended import JWTManager`
   2. Set up library config: 
    ```python
        app.config["JWT_COOKIE_SECURE"] = True
        app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
        app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
        app.config['JWT_ACCESS_COOKIE_PATH'] = f'/api/{general_api_version}'
        app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
        app.config['JWT_REFRESH_COOKIE_PATH'] = f'/api/{general_api_version}/refresh'
        app.config['JWT_COOKIE_CSRF_PROTECT'] = False
        app.config["JWT_SECRET_KEY"] = secrets.token_hex(16)
        jwt = JWTManager(app)
    ```
## How to Use It
## API Endpoint Docs

[Include documentation for API endpoints here]


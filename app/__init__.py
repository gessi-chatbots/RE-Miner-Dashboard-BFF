from flask import Flask
import logging
from app.users_api.routes import users_api_bp

app = Flask(__name__)

# Logging Configuration
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(logging.FileHandler('app.log'))

app.register_blueprint(users_api_bp, url_prefix='/users_api')


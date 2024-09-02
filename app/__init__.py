"""
This module initializes the Flask application and sets up Swagger for API documentation.
"""
import os
from flask import Flask
from flasgger import Swagger

# Create Flask application
app = Flask(__name__)

# Setting up Swagger configuration for API documentation
app.config['SWAGGER'] = {
    'title': 'Virtual Try-On API',
    'description': 'API for virtual try-on functionality.'
}

# Configuration for the results directory
app.config['RESULT_FOLDER'] = os.getenv('RESULT_FOLDER', 'results')

# Create the results directory if it doesn't exist
if not os.path.exists(app.config['RESULT_FOLDER']):
    os.makedirs(app.config['RESULT_FOLDER'])

# Configuration for the temp directory
app.config['TEMP_FOLDER'] = os.getenv('TEMP_FOLDER', 'temp')

# Create the temp directory if it doesn't exist
if not os.path.exists(app.config['TEMP_FOLDER']):
    os.makedirs(app.config['TEMP_FOLDER'])

swagger = Swagger(app)

# Import log configuration and apply to the app
from config.log_config import configure_logging, log_request_info, log_response_info
configure_logging(app)
log_request_info(app)
log_response_info(app)

# Import the routes module to register endpoints
from app import routes

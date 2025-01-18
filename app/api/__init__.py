# ./api/__init__.py
from flask import Flask
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    CORS(app)  # This applies CORS to all routes

    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default-secret-key')

    # Configure API base URL based on environment
    if os.environ.get('FLASK_ENV') == 'production':
        app.config['BASE_URL'] = '/dataviz/api'
    else:
        app.config['BASE_URL'] = ''

    # Register routes
    from .routes import bp  # Update this line
    app.register_blueprint(bp, url_prefix=app.config['BASE_URL'])

    return app

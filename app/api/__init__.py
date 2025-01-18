# ./api/__init__.py
from flask import Flask
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    CORS(app)  # This applies CORS to all routes
    
    # Configure API base URL based on environment
    if os.environ.get('FLASK_ENV') == 'production':
        app.config['BASE_URL'] = '/dataviz/api'
    else:
        app.config['BASE_URL'] = ''
        
    # Register routes
    from .api import routes
    app.register_blueprint(routes.bp, url_prefix=app.config['BASE_URL'])
    
    return app
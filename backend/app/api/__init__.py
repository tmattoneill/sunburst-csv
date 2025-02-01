# ./api/__init__.py
from flask import Flask
from flask_cors import CORS
import os


def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default-secret-key')

    # Use a simple path prefix for development
    app.config['BASE_URL'] = os.getenv('VUE_APP_API_ROOT_PATH', '/api')

    from .routes import bp
    app.register_blueprint(bp, url_prefix=app.config['BASE_URL'])

    return app

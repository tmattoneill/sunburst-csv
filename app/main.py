from api import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Get environment and port from environment variables
    flask_env = os.getenv('FLASK_ENV', 'prod')
    port = int(os.getenv('FLASK_PORT', 5001))

    # Enable debug mode if in development
    debug_mode = (flask_env == 'dev')

    app.run(debug=debug_mode, port=port)

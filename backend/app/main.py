from api import create_app
import os
from dotenv import load_dotenv

load_dotenv()
app = create_app()

if __name__ == '__main__':
    flask_env = os.getenv('FLASK_DEBUG', 1)
    port = int(os.getenv('FLASK_PORT', 6500))
    debug_mode = os.getenv('FLASK_DEBUG', 1)

    app.run(debug=debug_mode, port=port)
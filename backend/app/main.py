from api import create_app
import os
from dotenv import load_dotenv

# Load .env and then override with .env.dev if it exists
load_dotenv()
from dotenv import find_dotenv
load_dotenv(find_dotenv('.env.dev'), override=True)

app = create_app()

if __name__ == '__main__':
    flask_env = os.getenv('FLASK_DEBUG', 1)
    port = int(os.getenv('BACKEND_PORT', 6500))
    debug_mode = os.getenv('FLASK_DEBUG', 1)

    app.run(debug=debug_mode, port=port)

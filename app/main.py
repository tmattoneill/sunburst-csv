from api.api import app
import os

if __name__ == '__main__':
    port = int(os.getenv('BACKEND_PORT', 5001))
    app.run(debug=True, port=port)

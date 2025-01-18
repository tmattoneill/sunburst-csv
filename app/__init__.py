# Backend API and File Processing
import os

# No need for load_dotenv in Docker as env vars are set via docker-compose
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default-secret-key')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL', 'sqlite:///data/security.db')
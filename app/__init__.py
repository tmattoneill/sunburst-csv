# Backend API and File Processing
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env file

app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default-secret-key')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL', 'sqlite:///data/security.db')

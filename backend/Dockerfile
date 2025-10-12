# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app/ ./app
COPY data/ ./data

# Expose the backend port (default 6500, can be overridden with FLASK_PORT env var)
EXPOSE ${FLASK_PORT:-6500}

# Set working directory to app folder where the api module is
WORKDIR /app/app

# Run the Flask app using Gunicorn with environment variables
CMD sh -c "gunicorn --bind 0.0.0.0:${FLASK_PORT:-6500} 'api:create_app()'"

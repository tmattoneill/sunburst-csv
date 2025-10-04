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

# Expose the backend port
EXPOSE 6500

# Set working directory to app folder where the api module is
WORKDIR /app/app

# Run the Flask app using Gunicorn with environment variables
CMD ["gunicorn", "--bind", "0.0.0.0:6500", "api:create_app()"]

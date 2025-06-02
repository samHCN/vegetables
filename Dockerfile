# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED True
# Set the working directory in the container
ENV APP_HOME /app
WORKDIR $APP_HOME

# Install system dependencies that might be needed by Python packages
# Example: RUN apt-get update && apt-get install -y some-package

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY main.py .
COPY web/ ./web/
COPY templates/ ./templates/
COPY static/ ./static/


# Expose the port the app runs on
# This should match the port Gunicorn will listen on (and the PORT env var for the app)
EXPOSE 8080

# Define the command to run the application
# Use Gunicorn as the WSGI server
# The number of workers can be adjusted based on the expected load and available resources
# Ensure main:app points to your Flask app instance in main.py
CMD exec gunicorn --bind :8080 --workers 1 --threads 8 --timeout 0 main:app

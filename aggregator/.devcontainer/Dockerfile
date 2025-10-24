# Use an official Python base image
FROM python:3.10-slim

# Install system dependencies (for OpenCV & video)
RUN apt-get update && apt-get install -y \
    ffmpeg libsm6 libxext6 libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY ../requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files (for development this will be overridden by mount)
COPY .. /app

# Default command (used when you start container manually)
CMD ["python", "aggregator.py"]

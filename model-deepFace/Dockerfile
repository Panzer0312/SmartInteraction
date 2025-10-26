FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY model-deepFace.py .

# Expose no ports (this service just runs inference)
EXPOSE 8090
CMD ["python", "model-deepFace.py"]

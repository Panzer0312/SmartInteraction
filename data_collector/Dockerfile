FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY data_collector.py .

EXPOSE 5000
CMD ["python", "data_collector.py"]

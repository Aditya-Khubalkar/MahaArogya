# MahaArogya AI/ML Subsystem Backend Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for audio & build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    espeak espeak-ng espeak-ng-data \
    git curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cu128

# Copy application source code and models
COPY ai/ ./ai/
COPY src/ ./src/
COPY data/ ./data/

EXPOSE 8000

# Run FastAPI with Uvicorn
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]



# Use official Python runtime as base image
FROM python:3.10-slim

# Set working directory in container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY backend/ ./backend/
COPY ingestion/ ./ingestion/
COPY data/ ./data/
COPY chroma_db/ ./chroma_db/
COPY .env.example .env

# Expose port for FastAPI
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV API_HOST=0.0.0.0
ENV API_PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]

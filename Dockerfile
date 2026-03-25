# Use a Python 3.12 slim image for efficiency
FROM python:3.12-slim

# Install system dependencies for SQLite and C++ extensions
RUN apt-get update && apt-get install -y \
    build-essential \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install requirements first (to use Docker cache)
COPY requirements.txt .
RUN pip install --no-cache-dir \
    --default-timeout=1000 \
    -r requirements.txt

# Copy the rest of the application
COPY . .

# Create persistent directories for your RAG and Database
RUN mkdir -p /app/storage /app/data

# Environment variable for the API Key location
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
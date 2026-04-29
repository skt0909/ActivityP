# Use Python 3.12 for better package compatibility
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for building Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .

# Upgrade pip and install Python dependencies with exact versions
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PORT=5000

# Start with gunicorn (production WSGI server) that reads PORT from environment
CMD sh -c 'gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 4 --timeout 120 backend.app:app'

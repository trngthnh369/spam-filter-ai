FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('wordnet', quiet=True); nltk.download('omw-1.4', quiet=True)"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p artifacts data logs

# The artifacts directory should be mounted as a volume from host
# This ensures trained models persist and are shared between containers
VOLUME ["/app/artifacts"]

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run application with proper host binding
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
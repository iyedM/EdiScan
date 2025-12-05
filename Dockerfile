# ==========================================
# EdiScan - Dockerfile
# Multi-stage build for optimized image
# ==========================================

# Stage 1: Builder
FROM python:3.10-slim-bookworm AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY server/requirements-docker.txt .

# Install Python dependencies (CPU-only PyTorch = much smaller)
RUN pip install --no-cache-dir --user -r requirements-docker.txt

# ==========================================
# Stage 2: Runtime
FROM python:3.10-slim-bookworm AS runtime

LABEL maintainer="EdiScan"
LABEL description="OCR Intelligent - Extraction de texte par IA"
LABEL version="1.0"

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
        libzbar0 \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY server/ ./server/
COPY web/ ./web/

# Create directories for data
RUN mkdir -p uploads processed models

# Environment variables
ENV FLASK_APP=server/app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Run the application
CMD ["python", "server/app.py"]

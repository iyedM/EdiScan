FROM python:3.10-slim-bookworm

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (CPU-only for smaller size)
RUN pip install --no-cache-dir \
    flask>=2.3.0 \
    easyocr>=1.6.0 \
    opencv-python-headless>=4.5.0 \
    numpy>=1.24.0 \
    pillow>=9.5.0 \
    werkzeug>=2.3.0 \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    torch \
    torchvision

# Copy application
COPY server/ ./server/
COPY web/ ./web/

# Create directories
RUN mkdir -p uploads processed models

# Environment
ENV FLASK_APP=server/app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Hugging Face uses port 7860
EXPOSE 7860

# Run on HF port
CMD ["python", "-c", "import sys; sys.path.insert(0, '.'); from server.app import app; app.run(host='0.0.0.0', port=7860)"]


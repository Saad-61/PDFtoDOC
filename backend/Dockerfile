# Stage 1: Base Build & Runtime Environment
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies required for PyMuPDF, OpenCV, and compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root system user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /home/appuser/.pdf2docx_temp && \
    chown -R appuser:appuser /home/appuser

# Copy dependency manifest and install packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY . .

# Set permissions
RUN chown -R appuser:appuser /app

USER appuser

# Health probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

# AI Data Assistant Dockerfile
# Multi-stage build for smaller production image

# ================================
# Stage 1: Build Environment
# ================================
FROM python:3.11-slim-bullseye as builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set build arguments
ARG BUILD_DATE
ARG VERSION=1.0.0
ARG VCS_REF

# Set build environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# ================================
# Stage 2: Production Environment  
# ================================
FROM python:3.11-slim-bullseye as production

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r appuser && \
    useradd -r -g appuser -d /app -s /sbin/nologin -c "App User" appuser

# Set production environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/opt/venv/bin:$PATH"
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Create necessary directories
RUN mkdir -p /app/{data,static,uploads,logs,config,models,services,auth,utils} && \
    chown -R appuser:appuser /app

# Copy application files
COPY --chown=appuser:appuser . .

# Ensure static directory has proper permissions
RUN chmod -R 755 /app/static || true

# Add labels for better image management
LABEL maintainer="richardtekere02@gmail.com"
LABEL version="${VERSION}"
LABEL build-date="${BUILD_DATE}"
LABEL vcs-ref="${VCS_REF}"
LABEL description="AI Data Assistant - Intelligent data analysis platform"
LABEL org.label-schema.schema-version="1.0"
LABEL org.label-schema.build-date="${BUILD_DATE}"
LABEL org.label-schema.vcs-ref="${VCS_REF}"
LABEL org.label-schema.name="ai-data-assistant"
LABEL org.label-schema.description="AI-powered data analysis and visualization platform"
LABEL org.label-schema.version="${VERSION}"

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 8501

# Create startup script
COPY --chown=appuser:appuser <<'EOF' /app/start.sh
#!/bin/bash
set -e

echo "🚀 Starting AI Data Assistant..."

# Wait for database to be ready
echo "⏳ Waiting for database connection..."
while ! nc -z ${DB_HOST:-postgres} ${DB_PORT:-5432}; do
  echo "Waiting for database..."
  sleep 2
done
echo "✅ Database is ready!"

# Wait for Redis to be ready  
echo "⏳ Waiting for Redis connection..."
while ! nc -z ${REDIS_HOST:-redis} ${REDIS_PORT:-6379}; do
  echo "Waiting for Redis..."
  sleep 2
done
echo "✅ Redis is ready!"

# Run database initialization if needed
echo "🔧 Initializing application..."
if [ -f "setup.py" ]; then
    python setup.py --no-interaction || true
fi

echo "🌟 Starting Streamlit application..."
exec streamlit run app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false \
    --server.enableCORS=false \
    --server.enableXsrfProtection=true \
    --server.maxUploadSize=200
EOF

RUN chmod +x /app/start.sh

# Default command
CMD ["/app/start.sh"]

# ================================
# Stage 3: Development Environment (optional)
# ================================
FROM production as development

# Install development dependencies
USER root
RUN apt-get update && apt-get install -y \
    vim \
    nano \
    git \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Install development Python packages
RUN /opt/venv/bin/pip install \
    jupyter \
    ipython \
    black \
    flake8 \
    pytest \
    pytest-cov

# Switch back to app user
USER appuser

# Development environment variables
ENV ENVIRONMENT=development
ENV DEBUG=true
ENV LOG_LEVEL=DEBUG

# Override command for development
CMD ["streamlit", "run", "app.py", "--server.runOnSave=true", "--server.fileWatcherType=poll"]
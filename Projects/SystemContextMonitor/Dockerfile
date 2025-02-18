# Use multi-stage build for optimized image size
# Stage 1: Build frontend
FROM node:16-alpine as frontend-builder
WORKDIR /app/frontend

# Copy frontend dependencies
COPY frontend/package*.json ./
RUN npm install

# Copy frontend source
COPY frontend/ ./

# Build frontend
RUN npm run build

# Stage 2: Build backend
FROM python:3.9-slim as backend-builder
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy backend dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Stage 3: Final image
FROM python:3.9-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxinerama1 \
    libxi6 \
    libxrandr2 \
    libxcursor1 \
    libxss1 \
    && rm -rf /var/lib/apt/lists/*

# Copy backend dependencies from builder
COPY --from=backend-builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy frontend build
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Copy application code
COPY core/ /app/core/
COPY services/ /app/services/
COPY tests/ /app/tests/

# Create non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "services.context.api:app", "--host", "0.0.0.0", "--port", "8000"] 
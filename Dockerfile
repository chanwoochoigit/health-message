# Minimal Health Message Application Dockerfile
FROM python:3.12-alpine

WORKDIR /app

# Install essential packages and build dependencies
RUN apk add --no-cache \
    bash \
    nodejs \
    npm \
    gcc \
    musl-dev \
    linux-headers \
    curl \
    util-linux

# Copy application code
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expose ports
EXPOSE 3000 8000

# Start command
CMD ["reflex", "run", "--env", "prod", "--backend-host", "0.0.0.0"]

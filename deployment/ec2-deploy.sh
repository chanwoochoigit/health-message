#!/bin/bash

# Health Message App - EC2 Local Deployment Script
# Run this script directly on your EC2 instance after SSH'ing in
# Usage: ./ec2-deploy.sh [environment] [docker-registry]

set -e

ENVIRONMENT=${1:-"production"}
DOCKER_REGISTRY=${2:-""}
APP_NAME="health-message-app"
CONTAINER_NAME="hmsg-$ENVIRONMENT"
FRONTEND_PORT="3000"
BACKEND_PORT="8000"
CONFIG_FILE="/opt/health-message-app/config/db_config"

# Set ports based on environment
if [ "$ENVIRONMENT" = "production" ]; then
    HOST_FRONTEND_PORT="80"
    HOST_BACKEND_PORT="8080"
else
    HOST_FRONTEND_PORT="3000"
    HOST_BACKEND_PORT="8000"
fi

echo "🚀 Health Message App - EC2 Deployment"
echo "======================================="
echo "Environment: $ENVIRONMENT"
echo "Registry: $DOCKER_REGISTRY"
echo "Container: $CONTAINER_NAME"
echo "Ports: $HOST_FRONTEND_PORT->$FRONTEND_PORT, $HOST_BACKEND_PORT->$BACKEND_PORT"
echo ""

# Check required parameters
if [ -z "$DOCKER_REGISTRY" ]; then
    echo "❌ Docker registry required!"
    echo ""
    echo "Usage: ./ec2-deploy.sh [environment] [docker-registry]"
    echo "Example: ./ec2-deploy.sh production myusername"
    exit 1
fi

# Check if config file exists and source it
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Database configuration not found!"
    echo ""
    echo "Please run the database setup script first:"
    echo "./ec2-setup-db.sh your-secure-password"
    exit 1
fi

# Source the config file
source "$CONFIG_FILE"

if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL not found in config file!"
    echo "Please ensure the database setup script completed successfully."
    exit 1
fi

echo "✅ Database configuration loaded from $CONFIG_FILE"

# Install Docker if needed
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    sudo apt-get update -y
    sudo apt-get install -y docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    echo "⚠️  Docker installed. You may need to logout/login for docker group to take effect."
    echo "⚠️  Using sudo for Docker commands in this session..."
fi

# Check if user can run docker without sudo
if ! docker ps &>/dev/null; then
    echo "⚠️  Using sudo for Docker commands (user not in docker group yet)..."
    DOCKER_CMD="sudo docker"
else
    DOCKER_CMD="docker"
    echo "✅ Docker permissions OK"
fi

# Create app directory
sudo mkdir -p /opt/health-message-app
sudo chown $USER:$USER /opt/health-message-app
cd /opt/health-message-app

# Stop existing container
if $DOCKER_CMD ps -q -f name=$CONTAINER_NAME 2>/dev/null | grep -q .; then
    echo "🛑 Stopping existing container..."
    $DOCKER_CMD stop $CONTAINER_NAME || true
    $DOCKER_CMD rm $CONTAINER_NAME || true
fi

# Pull latest image
echo "📥 Pulling latest image..."
$DOCKER_CMD pull $DOCKER_REGISTRY/$APP_NAME:latest

# Create logs directory
mkdir -p logs

# Start new container
echo "🚀 Starting container..."
$DOCKER_CMD run -d \
    --name $CONTAINER_NAME \
    --network host \
    -e DATABASE_URL="$(grep DATABASE_URL $CONFIG_FILE | cut -d'=' -f2-)" \
    -e ENVIRONMENT="$ENVIRONMENT" \
    -v /opt/health-message-app/logs:/app/logs \
    -v $CONFIG_FILE:/app/config/db_config:ro \
    $DOCKER_REGISTRY/$APP_NAME:latest

# Wait and check
echo "⏳ Waiting for container to start..."
sleep 10

if $DOCKER_CMD ps -q -f name=$CONTAINER_NAME | grep -q .; then
    echo "✅ Container started successfully!"
    echo ""
    echo "📊 Container Status:"
    $DOCKER_CMD ps -f name=$CONTAINER_NAME --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    echo "🌐 Application URLs:"
    echo "  Frontend: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):$HOST_FRONTEND_PORT"
    echo "  Backend:  http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):$HOST_BACKEND_PORT"
    echo ""
    echo "📋 Useful commands:"
    echo "  View logs:    $DOCKER_CMD logs $CONTAINER_NAME -f"
    echo "  Restart:      $DOCKER_CMD restart $CONTAINER_NAME"
    echo "  Stop:         $DOCKER_CMD stop $CONTAINER_NAME"
    echo "  Shell access: $DOCKER_CMD exec -it $CONTAINER_NAME /bin/bash"
else
    echo "❌ Container failed to start!"
    echo ""
    echo "📋 Container logs:"
    $DOCKER_CMD logs $CONTAINER_NAME
    echo ""
    echo "🔍 Troubleshooting:"
    echo "1. Check if DATABASE_URL is correct"
    echo "2. Check if ports $HOST_FRONTEND_PORT and $HOST_BACKEND_PORT are available"
    echo "3. Check security group allows these ports"
    exit 1
fi

# Cleanup old images
echo "🧹 Cleaning up old images..."
$DOCKER_CMD image prune -f

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "Next steps:"
echo "1. Test your application at the URLs above"
echo "2. Set up your database if not done yet"
echo "3. Monitor logs with: $DOCKER_CMD logs $CONTAINER_NAME -f" 
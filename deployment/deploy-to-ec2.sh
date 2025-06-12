#!/bin/bash

# Health Message App - EC2 Deployment Script
# Usage: See README.md for environment variables needed

set -e

# Required environment variables
REQUIRED_VARS=("EC2_HOST" "EC2_USER" "PEM_KEY_PATH" "DOCKER_REGISTRY" "DATABASE_URL")

echo "🚀 Deploying Health Message App to EC2"
echo ""

# Check required environment variables
missing_vars=()
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ Missing required environment variables:"
    printf '   %s\n' "${missing_vars[@]}"
    echo ""
    echo "Example usage:"
    echo "export EC2_HOST=your-ec2-host"
    echo "export EC2_USER=ubuntu"
    echo "export PEM_KEY_PATH=./keys/your-key.pem"
    echo "export DOCKER_REGISTRY=your-username"
    echo "export DATABASE_URL=postgresql://user:pass@host:5432/db"
    echo "./deployment/deploy-to-ec2.sh"
    exit 1
fi

# Configuration
ENVIRONMENT=${1:-"production"}
APP_NAME="health-message-app"
CONTAINER_NAME="hmsg-$ENVIRONMENT"
FRONTEND_PORT="3000"
BACKEND_PORT="8000"

# Set ports based on environment
if [ "$ENVIRONMENT" = "production" ]; then
    HOST_FRONTEND_PORT="80"
    HOST_BACKEND_PORT="8080"
else
    HOST_FRONTEND_PORT="3000"
    HOST_BACKEND_PORT="8000"
fi

echo "Environment: $ENVIRONMENT"
echo "EC2 Host: $EC2_HOST"
echo "Container: $CONTAINER_NAME"
echo "Ports: $HOST_FRONTEND_PORT->$FRONTEND_PORT, $HOST_BACKEND_PORT->$BACKEND_PORT"
echo ""

# Validate PEM key
if [ ! -f "$PEM_KEY_PATH" ]; then
    echo "❌ PEM key file not found: $PEM_KEY_PATH"
    exit 1
fi

chmod 400 "$PEM_KEY_PATH"

# Test SSH connection
echo "🔌 Testing SSH connection..."
if ! ssh -i "$PEM_KEY_PATH" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" "echo 'SSH OK'" 2>/dev/null; then
    echo "❌ SSH connection failed"
    exit 1
fi

echo "✅ SSH connection successful"

# Create and execute deployment script on EC2
DEPLOY_SCRIPT="
#!/bin/bash
set -e

echo '📦 Setting up application on EC2...'

# Install Docker if needed
if ! command -v docker &> /dev/null; then
    echo '🐳 Installing Docker...'
    sudo apt-get update -y
    sudo apt-get install -y docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker \$USER
    echo '⚠️  Docker installed. You may need to logout/login for permissions to take effect.'
    echo '⚠️  Using sudo for Docker commands in this session...'
fi

# Check if user can run docker without sudo
if ! docker ps &>/dev/null; then
    echo '⚠️  Using sudo for Docker commands (user not in docker group yet)...'
    DOCKER_CMD='sudo docker'
else
    DOCKER_CMD='docker'
fi

# Create app directory
sudo mkdir -p /opt/health-message-app
sudo chown \$USER:\$USER /opt/health-message-app
cd /opt/health-message-app

# Stop existing container
if \$DOCKER_CMD ps -q -f name=$CONTAINER_NAME 2>/dev/null | grep -q .; then
    echo '🛑 Stopping existing container...'
    \$DOCKER_CMD stop $CONTAINER_NAME || true
    \$DOCKER_CMD rm $CONTAINER_NAME || true
fi

# Pull latest image
echo '📥 Pulling latest image...'
\$DOCKER_CMD pull $DOCKER_REGISTRY/$APP_NAME:latest

# Create logs directory
mkdir -p logs

# Start new container
echo '🚀 Starting container...'
\$DOCKER_CMD run -d \\
    --name $CONTAINER_NAME \\
    --restart unless-stopped \\
    -p $HOST_FRONTEND_PORT:$FRONTEND_PORT \\
    -p $HOST_BACKEND_PORT:$BACKEND_PORT \\
    -e DATABASE_URL='$DATABASE_URL' \\
    -e ENVIRONMENT='$ENVIRONMENT' \\
    -v /opt/health-message-app/logs:/app/logs \\
    $DOCKER_REGISTRY/$APP_NAME:latest

# Wait and check
echo '⏳ Waiting for container to start...'
sleep 10

if \$DOCKER_CMD ps -q -f name=$CONTAINER_NAME | grep -q .; then
    echo '✅ Container started successfully!'
    echo '🌐 Application URLs:'
    echo '  Frontend: http://$EC2_HOST:$HOST_FRONTEND_PORT'
    echo '  Backend:  http://$EC2_HOST:$HOST_BACKEND_PORT'
else
    echo '❌ Container failed to start!'
    \$DOCKER_CMD logs $CONTAINER_NAME
    exit 1
fi

# Cleanup old images
\$DOCKER_CMD image prune -f
echo '🎉 Deployment completed!'
"

# Execute deployment script on EC2
echo "📤 Executing deployment..."
ssh -i "$PEM_KEY_PATH" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" "$DEPLOY_SCRIPT"

echo ""
echo "🎉 Deployment completed successfully!"
echo "🌐 Your application is available at:"
echo "   Frontend: http://$EC2_HOST:$HOST_FRONTEND_PORT"
echo "   Backend:  http://$EC2_HOST:$HOST_BACKEND_PORT" 
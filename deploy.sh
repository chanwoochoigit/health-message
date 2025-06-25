#!/bin/bash

# ==============================================================================
# Unified Health Message Deployment Script
#
# This single script handles the entire deployment process:
# 1. Builds the Docker image locally.
# 2. Pushes the image to a Docker registry.
# 3. SSHs into the EC2 server and deploys the new container.
#
# USAGE:
#   1. Set the required environment variables (see below).
#   2. Run ./deploy.sh
# ==============================================================================

set -e

echo "🚀 Starting Unified Health Message Deployment"
echo "=========================================="

# --- Configuration ---
# Read all configuration from environment variables.
# Ensure these are set in your shell before running the script.
REQUIRED_VARS=(
    "DOCKER_REGISTRY"
    "EC2_HOST"
    "EC2_USER"
    "PEM_KEY_PATH"
    "DATABASE_URL"
    "API_URL"
)

APP_NAME="health-message-app"
CONTAINER_NAME="hmsg-production"
IMAGE_TAG="latest"
FULL_IMAGE_NAME="$DOCKER_REGISTRY/$APP_NAME:$IMAGE_TAG"

# --- Pre-flight Checks ---
echo "🔎 Checking prerequisites..."

# 1. Check for missing environment variables
missing_vars=()
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ Error: Missing required environment variables:"
    printf '   - %s\n' "${missing_vars[@]}"
    echo ""
    echo "💡 Please export them in your terminal. Example:"
    echo "   export DOCKER_REGISTRY=yourdockerhubusername"
    echo "   export EC2_HOST=ec2-xx-xx-xx-xx.compute-1.amazonaws.com"
    echo "   export EC2_USER=ubuntu"
    echo "   export PEM_KEY_PATH=./keys/your-key.pem"
    echo "   export DATABASE_URL='postgresql://user:pass@localhost:5432/db'"
    echo "   export API_URL='http://ec2-xx-xx-xx-xx.compute-1.amazonaws.com:8000'"
    exit 1
fi

# 2. Check for PEM key file
if [ ! -f "$PEM_KEY_PATH" ]; then
    echo "❌ Error: PEM key file not found at: $PEM_KEY_PATH"
    exit 1
fi
chmod 400 "$PEM_KEY_PATH"

echo "✅ Prerequisites met."
echo ""


# --- Step 1: Build and Push Docker Image ---
echo "STEP 1: Building and Pushing Docker Image"
echo "------------------------------------------"
echo "🔨 Building image: $FULL_IMAGE_NAME"

# The multi-stage build requires the API_URL at build time
# to correctly package the static frontend files.
docker build \
    --platform linux/amd64 \
    --build-arg API_URL="$API_URL" \
    --tag "$FULL_IMAGE_NAME" \
    .

echo "📤 Pushing image to Docker Hub..."
docker push "$FULL_IMAGE_NAME"

echo "✅ Image built and pushed successfully."
echo ""


# --- Step 2: Deploy to EC2 ---
echo "STEP 2: Deploying to EC2 Server"
echo "---------------------------------"
echo "Connecting to $EC2_HOST..."

# This script block will be executed remotely on the EC2 server.
REMOTE_SCRIPT="
#!/bin/bash
set -e

echo '   [EC2] 📦 Starting remote setup...'

# Define Docker command to handle sudo if needed
if ! docker ps &>/dev/null; then
    DOCKER_CMD='sudo docker'
else
    DOCKER_CMD='docker'
fi

echo '   [EC2] 📥 Pulling latest image: $FULL_IMAGE_NAME'
\$DOCKER_CMD pull $FULL_IMAGE_NAME

echo '   [EC2] 🛑 Stopping and removing existing container...'
\$DOCKER_CMD stop $CONTAINER_NAME || true
\$DOCKER_CMD rm $CONTAINER_NAME || true

echo '   [EC2] 🚀 Starting new application container...'
# The main application container's entrypoint script (run.sh) is now responsible
# for initializing the database tables before starting the servers.
# We also expose the frontend and backend ports.
\$DOCKER_CMD run -d \\
    --name $CONTAINER_NAME \\
    --restart unless-stopped \\
    -p 3000:3000 \\
    -p 8000:8000 \\
    -e DATABASE_URL='$DATABASE_URL' \\
    $FULL_IMAGE_NAME

echo '   [EC2] ✅ Remote deployment script finished.'
"

# Execute the remote script via SSH
ssh -i "$PEM_KEY_PATH" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" "${REMOTE_SCRIPT}"

echo "✅ Deployment command sent to EC2."
echo ""


# --- Final Summary ---
echo "🎉 DEPLOYMENT COMPLETE! 🎉"
echo "=========================="
echo "Your application should be available shortly at:"
echo "🌐 Frontend: http://$EC2_HOST:3000"
echo "⚡ Backend:  http://$EC2_HOST:8000"
echo ""
echo "To check status, run: ssh -i $PEM_KEY_PATH $EC2_USER@$EC2_HOST 'sudo docker ps'"
echo "To view logs, run:  ssh -i $PEM_KEY_PATH $EC2_USER@$EC2_HOST 'sudo docker logs -f $CONTAINER_NAME'"
echo "" 
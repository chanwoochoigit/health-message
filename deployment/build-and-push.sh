#!/bin/bash

# Health Message App - Docker Build and Push Script
# Usage: DOCKER_REGISTRY=username ./build-and-push.sh [tag]

set -e

# Configuration from environment variables
DOCKER_REGISTRY=${DOCKER_REGISTRY:-""}
APP_NAME="health-message-app"
TAG=${1:-"latest"}

if [ -z "$DOCKER_REGISTRY" ]; then
    echo "❌ Error: DOCKER_REGISTRY environment variable not set"
    echo "Usage: DOCKER_REGISTRY=your-username ./build-and-push.sh [tag]"
    echo "Example: DOCKER_REGISTRY=chanson76 ./build-and-push.sh v1.0"
    exit 1
fi

FULL_IMAGE_NAME="$DOCKER_REGISTRY/$APP_NAME:$TAG"

echo "🐳 Building Health Message Application"
echo "Registry: $DOCKER_REGISTRY"
echo "Image: $FULL_IMAGE_NAME"
echo "Platform: linux/amd64"
echo ""

# Build and push for amd64 only
echo "🔨 Building Docker image..."
docker build \
    --platform linux/amd64 \
    --tag $FULL_IMAGE_NAME \
    --tag $DOCKER_REGISTRY/$APP_NAME:latest \
    .

echo "📤 Pushing to registry..."
docker push $FULL_IMAGE_NAME
docker push $DOCKER_REGISTRY/$APP_NAME:latest

echo "✅ Build and push completed!"
echo "Image: $FULL_IMAGE_NAME" 
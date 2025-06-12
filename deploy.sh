#!/bin/bash

# Health Message App - Simple Deployment Script
# Usage: ./deploy.sh [help|setup|build|deploy|full] [environment]

set -e

COMMAND=${1:-"help"}
ENVIRONMENT=${2:-"production"}

echo "🚀 Health Message App Deployment"
echo ""

case $COMMAND in
    "setup")
        echo "🔧 Initial setup..."
        mkdir -p keys
        echo "✅ Created keys/ directory"
        echo ""
        echo "📝 Next steps:"
        echo "1. Copy your PEM key to keys/ directory"
        echo "2. Set environment variables (see examples below)"
        echo "3. Run: ./deploy.sh build"
        ;;

    "build")
        echo "🔨 Building and pushing Docker image..."
        if [ -z "$DOCKER_REGISTRY" ]; then
            echo "❌ DOCKER_REGISTRY not set"
            echo "Example: export DOCKER_REGISTRY=your-username"
            exit 1
        fi
        ./deployment/build-and-push.sh "$ENVIRONMENT"
        ;;

    "deploy")
        echo "🚀 Deploying to EC2..."
        ./deployment/deploy-to-ec2.sh "$ENVIRONMENT"
        ;;

    "database")
        echo "🗄️  Setting up database..."
        ./deployment/setup-database.sh local
        ;;

    "full")
        echo "🎯 Full deployment pipeline..."
        ./deployment/build-and-push.sh "$ENVIRONMENT"
        ./deployment/deploy-to-ec2.sh "$ENVIRONMENT"
        ;;

    "status")
        echo "📊 Checking status..."
        if [ -z "$EC2_HOST" ] || [ -z "$PEM_KEY_PATH" ]; then
            echo "❌ EC2_HOST and PEM_KEY_PATH must be set"
            exit 1
        fi
        ssh -i "$PEM_KEY_PATH" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" "docker ps"
        ;;

    "logs")
        echo "📋 Fetching logs..."
        if [ -z "$EC2_HOST" ] || [ -z "$PEM_KEY_PATH" ]; then
            echo "❌ EC2_HOST and PEM_KEY_PATH must be set"
            exit 1
        fi
        ssh -i "$PEM_KEY_PATH" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" "docker logs hmsg-$ENVIRONMENT -f"
        ;;

    "help"|*)
        echo "Commands:"
        echo "  setup     - Create directories"
        echo "  build     - Build and push Docker image"
        echo "  deploy    - Deploy to EC2"
        echo "  database  - Setup PostgreSQL on EC2"
        echo "  full      - Build + Deploy"
        echo "  status    - Check deployment status"
        echo "  logs      - View application logs"
        echo ""
        echo "Required Environment Variables:"
        echo "  DOCKER_REGISTRY  - Your Docker Hub username"
        echo "  EC2_HOST         - EC2 public IP or hostname"
        echo "  EC2_USER         - EC2 username (usually 'ubuntu')"
        echo "  PEM_KEY_PATH     - Path to your .pem key file"
        echo "  DATABASE_URL     - PostgreSQL connection string"
        echo ""
        echo "Example Setup:"
        echo "  export DOCKER_REGISTRY=myusername"
        echo "  export EC2_HOST=ec2-1-2-3-4.compute.amazonaws.com"
        echo "  export EC2_USER=ubuntu"
        echo "  export PEM_KEY_PATH=./keys/my-key.pem"
        echo "  export DATABASE_URL=postgresql://user:pass@localhost:5432/health_message_db"
        echo ""
        echo "  ./deploy.sh full"
        ;;
esac 
#!/bin/bash

# This script prepares the environment for a local Docker Compose build.
# It reads the .env file and creates the db_config file needed by the Dockerfile.

set -e

if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create one with your database credentials."
    exit 1
fi

# Source the .env file to get the variables
export $(grep -v '^#' .env | xargs)

echo "🔧 Generating db_config for local build..."

# IMPORTANT: The database host is 'db', which is the service name in docker-compose.yml.
# This allows the 'app' container to find the 'db' container on the Docker network.
cat > db_config << EOF
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
EOF

echo "✅ db_config generated successfully."
echo "You can now run 'docker compose build' and 'docker compose up'." 
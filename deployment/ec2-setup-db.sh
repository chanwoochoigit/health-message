#!/bin/bash

# Health Message App - EC2 Database Setup Script
# Run this script directly on your EC2 instance after SSH'ing in
# Usage: ./ec2-setup-db.sh [password]

set -e

DB_PASSWORD=${1:-""}
DB_NAME="health_message_db"
DB_USER="hmsg_user"

echo "🗄️  Health Message App - PostgreSQL Setup"
echo "=========================================="

if [ -z "$DB_PASSWORD" ]; then
    echo "❌ Please provide a database password!"
    echo ""
    echo "Usage: ./ec2-setup-db.sh your-secure-password"
    echo ""
    echo "Example:"
    echo "./ec2-setup-db.sh mySecurePass123"
    exit 1
fi

echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo "Password: [hidden]"
echo ""

# Install PostgreSQL
echo "📦 Installing PostgreSQL..."
sudo apt-get update -y
sudo apt-get install -y postgresql postgresql-contrib

# Start and enable PostgreSQL
echo "🔧 Starting PostgreSQL service..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Configure PostgreSQL
echo "🔧 Configuring PostgreSQL..."

# Create database and user
echo "👤 Creating database and user..."
sudo -u postgres createdb $DB_NAME || echo "Database already exists"
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" || echo "User already exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
sudo -u postgres psql -c "ALTER USER $DB_USER CREATEDB;"

# Configure for network access (for local connections)
echo "🌐 Configuring network access..."
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /etc/postgresql/*/main/postgresql.conf
echo "host all all 127.0.0.1/32 md5" | sudo tee -a /etc/postgresql/*/main/pg_hba.conf
echo "host all all ::1/128 md5" | sudo tee -a /etc/postgresql/*/main/pg_hba.conf

# Restart PostgreSQL to apply changes
echo "🔄 Restarting PostgreSQL..."
sudo systemctl restart postgresql

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to start..."
sleep 5

# Test connection with retry
echo "🔍 Testing database connection..."
for i in {1..5}; do
    if PGPASSWORD=$DB_PASSWORD psql -h localhost -U $DB_USER -d $DB_NAME -c "SELECT 1;" &>/dev/null; then
        echo "✅ Database connection successful!"
        break
    else
        if [ $i -eq 5 ]; then
            echo "❌ Database connection failed after 5 attempts!"
            echo "🔍 Debug info:"
            sudo systemctl status postgresql
            echo ""
            echo "Try connecting manually:"
            echo "PGPASSWORD=$DB_PASSWORD psql -h localhost -U $DB_USER -d $DB_NAME"
            exit 1
        else
            echo "⏳ Attempt $i failed, retrying in 2 seconds..."
            sleep 2
        fi
    fi
done

echo ""
echo "🎉 PostgreSQL setup completed successfully!"
echo ""
echo "📋 Database Details:"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  Database: $DB_NAME"
echo "  Username: $DB_USER"
echo "  Password: $DB_PASSWORD"
echo ""
echo "🔗 DATABASE_URL for your application:"
echo "export DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
echo ""
echo "📝 Next steps:"
echo "1. Set the DATABASE_URL environment variable (see above)"
echo "2. Run the deployment script: ./ec2-deploy.sh"
echo ""
echo "💡 Useful PostgreSQL commands:"
echo "  Connect to DB: PGPASSWORD=$DB_PASSWORD psql -h localhost -U $DB_USER -d $DB_NAME"
echo "  Check status:  sudo systemctl status postgresql"
echo "  View logs:     sudo journalctl -u postgresql -f" 
#!/bin/bash

# Health Message App - Database Setup Script
# Usage: See README.md for environment variables needed

set -e

# Required environment variables for local setup
if [ "${1:-local}" = "local" ]; then
    REQUIRED_VARS=("EC2_HOST" "EC2_USER" "PEM_KEY_PATH")
    
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
        echo "export DB_PASSWORD=your-secure-database-password"
        echo "./deployment/setup-database.sh local"
        exit 1
    fi
fi

DB_TYPE=${1:-"local"}
DB_NAME="health_message_db"
DB_USER="hmsg_user"
DB_PASSWORD=${DB_PASSWORD:-"CHANGE_THIS_SECURE_PASSWORD"}

echo "🗄️  Setting up PostgreSQL Database"
echo "Type: $DB_TYPE"
echo ""

case $DB_TYPE in
    "local")
        echo "Setting up PostgreSQL on EC2..."
        
        # Validate PEM key
        if [ ! -f "$PEM_KEY_PATH" ]; then
            echo "❌ PEM key file not found: $PEM_KEY_PATH"
            exit 1
        fi
        
        chmod 400 "$PEM_KEY_PATH"
        
        # Create database setup script
        DB_SETUP="
#!/bin/bash
set -e

echo '📦 Installing PostgreSQL...'
sudo apt-get update -y
sudo apt-get install -y postgresql postgresql-contrib

echo '🔧 Configuring PostgreSQL...'
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres createdb $DB_NAME || echo 'Database exists'
sudo -u postgres psql -c \"CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';\" || echo 'User exists'
sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;\"
sudo -u postgres psql -c \"ALTER USER $DB_USER CREATEDB;\"

# Configure for network access
sudo sed -i \"s/#listen_addresses = 'localhost'/listen_addresses = '*'/\" /etc/postgresql/*/main/postgresql.conf
echo 'host all all 0.0.0.0/0 md5' | sudo tee -a /etc/postgresql/*/main/pg_hba.conf
sudo systemctl restart postgresql

echo '✅ PostgreSQL setup completed!'
echo 'Connection: postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME'
"

        # Execute on EC2
        echo "📤 Installing PostgreSQL on EC2..."
        ssh -i "$PEM_KEY_PATH" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" "$DB_SETUP"

        echo ""
        echo "✅ Local PostgreSQL setup completed!"
        echo "🔗 Use this DATABASE_URL:"
        echo "   postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
        ;;

    "rds")
        echo "📋 RDS Setup Instructions:"
        echo ""
        echo "1. 🌐 Create RDS PostgreSQL instance in AWS Console"
        echo "2. 🔒 Configure security group to allow access from EC2"
        echo "3. 🔗 Use this format for DATABASE_URL:"
        echo "   postgresql://username:password@rds-endpoint:5432/$DB_NAME"
        echo ""
        echo "💡 RDS Benefits: Automated backups, high availability, monitoring"
        echo "💰 Cost: ~\$15-25/month for db.t3.micro"
        ;;

    *)
        echo "❌ Unknown database type: $DB_TYPE"
        echo "Usage: $0 [local|rds]"
        exit 1
        ;;
esac

echo ""
echo "🔍 Next steps:"
echo "1. Update deployment/deploy-to-ec2.sh with your database URL"
echo "2. Test database connection from your application"
echo "3. Run your deployment script: ./deployment/deploy-to-ec2.sh" 
# Health Message Application
## ✨ Features

### 🔐 Authentication System
- **Secure login/registration** with bcrypt password hashing
- **Role-based access** - Doctor and Patient profiles
- **Automatic redirects** based on user role

### 👨‍⚕️ Doctor Dashboard
- **Patient Statistics** - Total patients, target achievements, chatbot success rates
- **Heart Rate Monitoring** - Visual charts of patient heart rate data
- **Age Demographics** - Patient age group distribution
- **Patient Management** - Comprehensive patient list with details
- **Modern UI** - Professional sidebar navigation and responsive design

### 🏥 Patient Portal
- **Personalized welcome** with user profile information
- **Future features** - Health tracking, messaging (coming soon)

## 🛠️ Technology Stack

- **Frontend**: Reflex (Modern Python web framework)
- **Backend**: Python with SQLAlchemy ORM
- **Database**: PostgreSQL (with SQLite fallback)
- **Security**: bcrypt password hashing with salt
- **UI**: Responsive design with professional styling

## 📁 Project Structure

```
hmsg/
├── services/           # Business logic & database operations
│   ├── database.py     # Database models and configuration
│   ├── auth_service.py # Authentication functions
│   └── patient_service.py # Patient data management
├── pages/              # UI pages and components
│   ├── auth.py         # Login/registration page
│   ├── dashboard.py    # Doctor dashboard with charts
│   ├── patient.py      # Patient portal
│   └── patients.py     # Patient management page
├── components/         # Reusable UI components
└── hmsg.py            # Main application entry point
```

## 🚀 Local Development

This project uses Docker Compose for a consistent and easy-to-manage local development environment.

### 1. Prerequisites
- Docker and Docker Compose installed.

### 2. Create Environment File
Create a `.env` file in the project root. This file is for local development only and is ignored by Git.
```bash
# The username for the local Postgres database.
POSTGRES_USER=myuser

# The password for the local Postgres database.
POSTGRES_PASSWORD=mypassword

# The name of the local Postgres database.
POSTGRES_DB=health_message_db

# The local port to access the database (optional, defaults to 5432).
DB_PORT=5432

# The local port to access the application's frontend.
APP_PORT=3000
```

### 3. Build and Run
With the `.env` file in place, run Docker Compose:
```bash
docker-compose up --build -d
```
- The `db` service will start a PostgreSQL container.
- The `db-init` service will run once to create the database tables and seed them with sample patients, then exit.
- The `app` service will build the application image and start the web server.

Your application is now running at **http://localhost:3000**.

To stop the services, run `docker-compose down`. To remove the database volume and start fresh, use `docker-compose down -v`.


## ☁️ Production Deployment (EC2)

This guide covers deploying the application to a single EC2 instance running Ubuntu.

### 1. One-Time Server Setup

Log in to your EC2 instance and perform these steps once:

**A. Install PostgreSQL:**
```bash
sudo apt-get update -y
sudo apt-get install -y postgresql postgresql-contrib docker.io
```

**B. Start and Enable Services:**
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo systemctl start docker
sudo systemctl enable docker
```

**C. Create Database and User:**
Choose a secure password and run the following commands, replacing `your_secure_password` with your choice.
```bash
DB_NAME="health_message_db"
DB_USER="hmsg_user"
DB_PASSWORD="your_secure_password"

sudo -u postgres createdb "$DB_NAME"
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE \"$DB_NAME\" TO $DB_USER;"
```

**D. Configure EC2 Security Group:**
Ensure your EC2 instance's security group allows inbound traffic on:
- **Port 22** (SSH) from your IP address.
- **Port 80** (HTTP) from anywhere (`0.0.0.0/0`).

### 2. Deployment

The deployment process is handled by a single script, `deploy.sh`. This is run from your **local machine**, not the EC2 server.

**A. Set Environment Variables:**
On your local machine, export the following variables. You can add these to your `~/.bashrc` or `~/.zshrc` for convenience.

```bash
# Your Docker Hub username or organization.
export DOCKER_REGISTRY="yourdockerhubusername"

# The public IP address or DNS name of your EC2 instance.
export EC2_HOST="ec2-xx-xx-xx-xx.compute-1.amazonaws.com"

# The user to log into your EC2 instance with (usually 'ubuntu').
export EC2_USER="ubuntu"

# The local path to your .pem key for EC2 access.
export PEM_KEY_PATH="./keys/your-key.pem"

# The full connection string for your PostgreSQL database on the EC2 server.
# NOTE: The host is 'localhost' because the app container will run on the
# same machine as the database, using the host network.
export DATABASE_URL="postgresql://hmsg_user:your_secure_password@localhost:5432/health_message_db"

# The public URL of your application's backend. This must match your EC2_HOST.
export API_URL="http://ec2-xx-xx-xx-xx.compute-1.amazonaws.com:8000"
```

**B. Run the Deployment Script:**
Make sure the script is executable, then run it:
```bash
chmod +x deploy.sh
./deploy.sh
```

The script will automatically build the Docker image, push it to your registry, SSH into your server, and start the new container.

### 3. Verifying the Deployment
The script will output the final URLs. To check the status or view logs directly:
```bash
# Check container status on EC2
ssh -i $PEM_KEY_PATH $EC2_USER@$EC2_HOST 'sudo docker ps'

# View live logs from the application
ssh -i $PEM_KEY_PATH $EC2_USER@$EC2_HOST 'sudo docker logs -f hmsg-production'
```
---
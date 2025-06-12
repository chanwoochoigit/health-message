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

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Database Setup

The setup script will automatically:
- Create PostgreSQL database if available
- Fall back to SQLite if PostgreSQL isn't available
- Create all necessary tables
- Optionally create sample patient data for testing (no user credentials)

```bash
python setup_database.py
```

### 3. Run Application

```bash
reflex run
```

Open your browser to `http://localhost:3000`

## 🔧 Manual PostgreSQL Setup (Optional)

If you prefer to set up PostgreSQL manually:

### Install PostgreSQL

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Ubuntu/Linux:**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### Database Configuration

The application automatically uses your system username for PostgreSQL connection.
To use custom credentials, set the environment variable:

```bash
export DATABASE_URL="postgresql://your_username:your_password@localhost:5432/health_message_db"
```

## 👥 User Registration

The application requires user registration for security. No default users are created.

To get started:
1. Run the application: `reflex run`
2. Click "Register" to create a new account
3. Choose your profile type (Doctor or Patient)

## 📊 Dashboard Features

### Statistics Cards
- **Total Patients** - Real-time count of registered patients
- **Target Achievement** - Percentage of patients meeting health goals
- **Chatbot Success** - AI persuasion effectiveness metrics

### Charts & Analytics
- **Heart Rate Monitoring** - Interactive bar charts showing patient vital signs
- **Age Distribution** - Demographic breakdown of patient population
- **Patient Details** - Comprehensive patient information table

## 🗃️ Database Schema

### Users Table
- `id` - Primary key
- `name` - Username (unique)
- `profile` - User type (doc/patient)
- `password_hash` - bcrypt hashed password
- `created_at` - Registration timestamp

### Patients Table
- `id` - Primary key
- `user_id` - Foreign key to users table
- `username` - Username (unique)
- `name` - User's name
- `age` - Patient age
- `target_achieved` - Health goal status
- `last_heart_rate` - Most recent vital signs
- `created_at` - Record creation timestamp

# local test build and run

```bash
python setup_database.py
export DB_USER=$(whoami)
docker build -t health-message-test .    
docker run \
  -e DATABASE_URL="postgresql://${DB_USER}@host.docker.internal:5432/health_message_db" \
  -p 3000:3000 -p 8000:8000 \
  health-message-test
```


# 🚀 Deployment

Clean deployment to EC2 using environment variables only.

## 🔧 Prerequisites

- Docker Hub account
- EC2 instance running Ubuntu
- PEM key file for SSH access

## 📋 Quick Start

### 1. Set Environment Variables

```bash
export DOCKER_REGISTRY=your-dockerhub-username
export EC2_HOST=your-ec2-ip-or-hostname
export EC2_USER=ubuntu
export PEM_KEY_PATH=./keys/your-key.pem
export DATABASE_URL=postgresql://user:pass@localhost:5432/health_message_db
export DB_PASSWORD=your-secure-database-password
```

### 2. Initial Setup
```bash
chmod +x deploy.sh deployment/*.sh
```

```bash
# Create keys directory and copy your PEM key
./deploy.sh setup
cp /path/to/your-key.pem keys/

# Set up database on EC2
./deploy.sh database

# Full deployment (build + deploy)
./deploy.sh full
```

## 🛠️ Commands

```bash
./deploy.sh setup      # Create directories
./deploy.sh build      # Build and push Docker image
./deploy.sh deploy     # Deploy to EC2
./deploy.sh database   # Setup PostgreSQL on EC2
./deploy.sh full       # Build + Deploy
./deploy.sh status     # Check deployment status
./deploy.sh logs       # View application logs
```

## 🗄️ Database Options

### Local PostgreSQL on EC2
```bash
export DB_PASSWORD=your-secure-database-password
./deploy.sh database
```

### AWS RDS
```bash
./deployment/setup-database.sh rds
# Follow printed instructions
```

## 🔍 Verification

Your app will be available at:
- **Production**: `http://your-ec2-ip` (port 80)
- **Staging**: `http://your-ec2-ip:3000`

## 🚨 Troubleshooting

```bash
# Check container status
./deploy.sh status

# View logs
./deploy.sh logs

# SSH into EC2
ssh -i $PEM_KEY_PATH $EC2_USER@$EC2_HOST

# Check containers manually
docker ps
docker logs hmsg-production
```

## 💡 Tips

- Keep your PEM key secure with `chmod 400`
- Use strong passwords for database
- Monitor your application with `./deploy.sh status`
- Set up CloudWatch for production monitoring

---
# 🖥️ Direct EC2 Deployment

Simple deployment by running scripts directly on your EC2 instance.

## 🚀 Quick Deployment

### 1. SSH into your EC2 instance

```bash
ssh -i keys/your-key.pem ubuntu@your-ec2-hostname
```

### 2. Move the deployment scripts
```bash
# From your local machine
export DOCKER_REGISTRY=your-username
./deployment/build-and-push.sh
scp -i keys/your-key.pem deployment/ec2-*.sh ubuntu@your-ec2-ip:~/
```

### 3. Set up the database

```bash
./ec2-setup-db.sh your-secure-password
```

### 4. Set the database URL

```bash
export DATABASE_URL=postgresql://hmsg_user:your-secure-password@localhost:5432/health_message_db
```

### 5. Deploy the application

```bash
sudo DATABASE_URL="$DATABASE_URL" bash ec2-deploy.sh production your-docker-registry
```

That's it! Your app will be running at `http://your-ec2-ip`

## 🛠️ Commands

### Database Setup:
```bash
./ec2-setup-db.sh your-password    # Set up PostgreSQL
```

### Application Deployment:
```bash
./ec2-deploy.sh production myregistry    # Deploy production
./ec2-deploy.sh staging myregistry       # Deploy staging environment
```

### Management:
```bash
# View logs
sudo docker logs hmsg-production -f

# Restart application
sudo docker restart hmsg-production

# Check status
sudo docker ps

# Stop application
sudo docker stop hmsg-production
```

## 🔧 Environment Variables

Set these before deploying:

```bash
export DATABASE_URL=postgresql://user:pass@host:5432/db
```

## 📊 Access Your App

- **Production**: `http://your-ec2-ip` (port 80)
- **Staging**: `http://your-ec2-ip:3000`

## 🚨 Troubleshooting

### Check application logs:
```bash
sudo docker logs hmsg-production
```

### Check database:
```bash
sudo systemctl status postgresql
PGPASSWORD=yourpass psql -h localhost -U hmsg_user -d health_message_db
```

### Check Docker:
```bash
sudo docker ps
sudo docker images
```

### Restart everything:
```bash
sudo systemctl restart postgresql
sudo docker restart hmsg-production
```
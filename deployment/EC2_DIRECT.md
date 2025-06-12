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
# while in EC2 instance
./ec2-setup-db.sh your-secure-password
```

### 4. Set the database URL

```bash
export DATABASE_URL=postgresql://hmsg_user:your-secure-password@localhost:5432/health_message_db
```

### 5. Deploy the application (porting to 9000 is required)
Note: The application will be available on port 9000 (changed from port 80 to avoid conflicts)
```bash
export HOST_FRONTEND_PORT=9000
export HOST_BACKEND_PORT=9001
sudo DATABASE_URL="$DATABASE_URL" bash ec2-deploy.sh production {your-docker-registry}

# if this still doesn't work try:
sudo docker run -d \
    --name hmsg-production \
    --restart unless-stopped \
    -p 9000:3000 \
    -p 9001:8000 \
    -e DATABASE_URL="$DATABASE_URL" \
    -e ENVIRONMENT="production" \
    {your-docker-registry}/health-message-app:latest
```


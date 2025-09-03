# YGG Torrent API - Docker Deployment

This guide explains how to deploy the YGG Torrent API using Docker and Docker Compose.

## 🐳 Quick Start

### Prerequisites
- Docker (version 20.10+)
- Docker Compose (version 2.0+)

### 1. Clone and Build
```bash
git clone <repository-url>
cd YGGparser
```

### 2. Run with Docker Compose
```bash
# Build and start the container
docker-compose up -d

# Or use the provided script
./docker-run.sh
```

### 3. Test the API
```bash
# Health check
curl http://localhost:8080/health

# Authenticate
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"your_username","password":"your_password"}'
```

## 📋 Docker Commands

### Build and Run
```bash
# Build the image
docker-compose build

# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### Manual Docker Commands
```bash
# Build image
docker build -t ygg-torrent-api .

# Run container
docker run -d \
  --name ygg-api \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --env-file docker.env \
  ygg-torrent-api

# View logs
docker logs -f ygg-api

# Stop container
docker stop ygg-api
docker rm ygg-api
```

## 🔧 Configuration

### Environment Variables
The following environment variables are available in `docker.env`:

- `PYTHONUNBUFFERED=1` - Python output buffering
- `DISPLAY=:99` - X11 display for headless mode
- `DOCKER_CONTAINER=true` - Enables Docker-specific optimizations
- `CHROME_BIN=/usr/bin/google-chrome` - Chrome binary path
- `CHROME_PATH=/usr/bin/google-chrome` - Chrome path

### Volumes
- `./data:/app/data` - Persistent storage for cookies and data
- `./logs:/app/logs` - Log files

### Ports
- `8080:8080` - API server port

## 🏗️ Docker Image Details

### Base Image
- `python:3.9-slim` - Lightweight Python 3.9 image

### Installed Packages
- Google Chrome (latest stable)
- Python dependencies from `requirements_api.txt`
- System libraries for Chrome headless operation

### Security Features
- Non-root user (`ygguser`)
- Minimal attack surface
- Resource limits

## 🚀 Production Deployment

### Using Docker Compose (Recommended)
```bash
# Production deployment
docker-compose -f docker-compose.yml up -d

# With custom environment
docker-compose -f docker-compose.yml --env-file production.env up -d
```

### Using Docker Swarm
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml ygg-api
```

### Using Kubernetes
```yaml
# Example Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ygg-torrent-api
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ygg-torrent-api
  template:
    metadata:
      labels:
        app: ygg-torrent-api
    spec:
      containers:
      - name: ygg-api
        image: ygg-torrent-api:latest
        ports:
        - containerPort: 8080
        env:
        - name: DOCKER_CONTAINER
          value: "true"
        volumeMounts:
        - name: data-volume
          mountPath: /app/data
        - name: logs-volume
          mountPath: /app/logs
      volumes:
      - name: data-volume
        persistentVolumeClaim:
          claimName: ygg-data-pvc
      - name: logs-volume
        persistentVolumeClaim:
          claimName: ygg-logs-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: ygg-torrent-api-service
spec:
  selector:
    app: ygg-torrent-api
  ports:
  - port: 8080
    targetPort: 8080
  type: LoadBalancer
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Chrome Installation Fails
```bash
# Check if Chrome is installed
docker exec -it ygg-torrent-api google-chrome --version

# Rebuild with verbose output
docker-compose build --no-cache
```

#### 2. Permission Issues
```bash
# Fix volume permissions
sudo chown -R 1000:1000 data logs

# Or run as root (not recommended for production)
docker run --user root ...
```

#### 3. Memory Issues
```bash
# Increase memory limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 4G
```

#### 4. Network Issues
```bash
# Check container network
docker network ls
docker network inspect yggparser_default

# Test connectivity
docker exec -it ygg-torrent-api curl -f http://localhost:8080/health
```

### Debugging

#### View Container Logs
```bash
# All logs
docker-compose logs

# Follow logs
docker-compose logs -f

# Specific service
docker-compose logs ygg-api
```

#### Access Container Shell
```bash
# Interactive shell
docker exec -it ygg-torrent-api /bin/bash

# Check Chrome installation
docker exec -it ygg-torrent-api google-chrome --version

# Test authentication manually
docker exec -it ygg-torrent-api python -c "
import undetected_chromedriver as uc
driver = uc.Chrome()
print('Chrome driver works!')
driver.quit()
"
```

#### Health Check
```bash
# Manual health check
curl -f http://localhost:8080/health

# Check container health
docker ps
docker inspect ygg-torrent-api | grep -A 10 Health
```

## 📊 Monitoring

### Resource Usage
```bash
# Container stats
docker stats ygg-torrent-api

# Resource limits
docker inspect ygg-torrent-api | grep -A 20 Resources
```

### Log Monitoring
```bash
# Real-time logs
docker-compose logs -f --tail=100

# Log rotation (add to docker-compose.yml)
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## 🔒 Security Considerations

### Production Security
1. **Use HTTPS**: Deploy behind a reverse proxy with SSL
2. **Network Security**: Use Docker networks and firewalls
3. **Secrets Management**: Use Docker secrets or external secret managers
4. **Regular Updates**: Keep base images and dependencies updated
5. **Resource Limits**: Set appropriate CPU and memory limits

### Example Nginx Reverse Proxy
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📈 Scaling

### Horizontal Scaling
```yaml
# docker-compose.yml with multiple replicas
version: '3.8'
services:
  ygg-api:
    build: .
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
    # ... rest of configuration
```

### Load Balancer
```yaml
# Add nginx load balancer
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - ygg-api
```

## 🎯 Performance Optimization

### Docker Optimizations
1. **Multi-stage builds** for smaller images
2. **Layer caching** for faster builds
3. **Resource limits** to prevent resource exhaustion
4. **Health checks** for automatic recovery

### Application Optimizations
1. **Connection pooling** for database connections
2. **Caching** for frequently accessed data
3. **Async processing** for long-running tasks
4. **Monitoring** and alerting

## 📝 Maintenance

### Regular Tasks
```bash
# Update base image
docker-compose pull
docker-compose up -d

# Clean up unused images
docker image prune

# Backup data
tar -czf ygg-backup-$(date +%Y%m%d).tar.gz data/ logs/

# Update dependencies
docker-compose build --no-cache
```

### Monitoring Script
```bash
#!/bin/bash
# health-monitor.sh
while true; do
    if ! curl -f http://localhost:8080/health > /dev/null 2>&1; then
        echo "API is down, restarting..."
        docker-compose restart ygg-api
    fi
    sleep 60
done
```

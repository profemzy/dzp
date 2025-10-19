# 🐳 Docker Deployment Guide

Complete guide for deploying DZP IAC Agent using Docker and Docker Compose.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Deployment Options](#deployment-options)
- [Service Architecture](#service-architecture)
- [Volume Management](#volume-management)
- [Networking](#networking)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)

---

## 🚀 Quick Start

### 1. Clone and Configure

```bash
# Clone the repository
git clone <repository-url>
cd dzp

# Copy environment file
cp .env.docker .env

# Edit .env with your configuration
nano .env
```

### 2. Start All Services

```bash
# Start web interface and API
docker-compose up -d

# View logs
docker-compose logs -f

# Access services:
# - Web Interface: http://localhost:8080
# - API Server: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### 3. Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## 📦 Prerequisites

### Required

- **Docker**: 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose**: 2.0+ ([Install Compose](https://docs.docker.com/compose/install/))
- **Terraform files**: Your `.tf` configuration files

### Optional

- **Ollama**: For local AI models (included in compose file)
- **GPU support**: For faster local AI inference

---

## ⚙️ Configuration

### Environment Variables

Create `.env` from `.env.docker`:

```bash
cp .env.docker .env
```

#### Key Configuration Options:

```env
# Choose your AI provider
AI_PROVIDER=openai_compatible  # or "openai"

# For OpenAI
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o

# For Ollama (running in Docker)
OPENAI_COMPATIBLE_BASE_URL=http://ollama:11434/v1
OPENAI_COMPATIBLE_MODEL=llama3.1

# Terraform files location on host
HOST_TERRAFORM_DIR=./terraform

# Enable advanced features
USE_DEEPAGENTS=false
HUMAN_IN_THE_LOOP=true
```

### Terraform Files

Place your Terraform files in the directory specified by `HOST_TERRAFORM_DIR`:

```bash
mkdir -p ./terraform
cp your-terraform-files/*.tf ./terraform/
```

---

## 🏗️ Deployment Options

### Option 1: Web Interface Only

Best for interactive use with browser UI:

```bash
docker-compose up web
```

Access at: http://localhost:8080

### Option 2: API Server Only

Best for programmatic access:

```bash
docker-compose up api
```

Access at: http://localhost:8000

### Option 3: All Services (Recommended)

Web interface + API + Ollama (optional):

```bash
# Without Ollama
docker-compose up -d

# With Ollama for local AI
docker-compose --profile with-ollama up -d
```

### Option 4: Custom Configuration

Use environment variables to override defaults:

```bash
docker-compose up -d \
  -e AI_PROVIDER=openai \
  -e OPENAI_API_KEY=your_key \
  -e TERRAFORM_DIR=/custom/path
```

---

## 🏛️ Service Architecture

### Services Overview

| Service | Port | Description | Command |
|---------|------|-------------|---------|
| **web** | 8080 | Full web interface + API | `dzp-web` |
| **api** | 8000 | Standalone REST API | `dzp-api` |
| **ollama** | 11434 | Local AI models (optional) | N/A |

### Service Details

#### Web Interface Container

```yaml
Container Name: dzp-web
Exposed Ports: 8080
Health Check: http://localhost:8080/api/health
Volumes:
  - ./terraform:/terraform (Terraform files)
  - web-sessions:/app/sessions (Session data)
```

#### API Server Container

```yaml
Container Name: dzp-api
Exposed Ports: 8000
Health Check: http://localhost:8000/health
Volumes:
  - ./terraform:/terraform (Terraform files)
  - api-sessions:/app/sessions (Session data)
```

#### Ollama Container (Optional)

```yaml
Container Name: dzp-ollama
Exposed Ports: 11434
Volumes:
  - ollama-data:/root/.ollama (Model storage)
Profile: with-ollama
```

---

## 💾 Volume Management

### Persistent Volumes

```bash
# List volumes
docker volume ls | grep dzp

# Inspect volume
docker volume inspect dzp_web-sessions

# Backup sessions
docker run --rm -v dzp_web-sessions:/data -v $(pwd):/backup \
  alpine tar czf /backup/sessions-backup.tar.gz -C /data .

# Restore sessions
docker run --rm -v dzp_web-sessions:/data -v $(pwd):/backup \
  alpine tar xzf /backup/sessions-backup.tar.gz -C /data
```

### Terraform Files

Your Terraform files are mounted as a volume from your host machine:

```yaml
volumes:
  - ${HOST_TERRAFORM_DIR:-./terraform}:/terraform
```

To change the location, update `HOST_TERRAFORM_DIR` in `.env`:

```env
HOST_TERRAFORM_DIR=/path/to/your/terraform/files
```

---

## 🌐 Networking

### Network Configuration

All services run on the `dzp-network` bridge network:

```bash
# Inspect network
docker network inspect dzp_dzp-network

# Services can communicate using container names:
# - http://api:8000 (from web container)
# - http://web:8080 (from api container)
# - http://ollama:11434 (from any container)
```

### Port Mapping

```yaml
Host Port → Container Port
8080 → 8080  (Web Interface)
8000 → 8000  (API Server)
11434 → 11434 (Ollama)
```

To change ports, edit `docker-compose.yml`:

```yaml
ports:
  - "9090:8080"  # Access web on port 9090
```

---

## 🔍 Troubleshooting

### Check Service Status

```bash
# View all running containers
docker-compose ps

# Check logs
docker-compose logs web
docker-compose logs api
docker-compose logs ollama

# Follow logs in real-time
docker-compose logs -f --tail=100
```

### Common Issues

#### 1. Cannot Connect to AI Provider

```bash
# Check environment variables
docker-compose exec web env | grep -i api

# Test connection from container
docker-compose exec web curl http://ollama:11434/api/tags
```

**Solution**: Verify `OPENAI_COMPATIBLE_BASE_URL` in `.env`

#### 2. Terraform Files Not Found

```bash
# Check if volume is mounted correctly
docker-compose exec web ls -la /terraform

# Verify host directory
ls -la ./terraform
```

**Solution**: Ensure `HOST_TERRAFORM_DIR` points to correct directory

#### 3. Permission Denied

```bash
# Check volume permissions
docker-compose exec web ls -l /terraform
```

**Solution**: Ensure terraform files are readable:
```bash
chmod -R 755 ./terraform
```

#### 4. Container Won't Start

```bash
# View detailed logs
docker-compose logs web

# Check if port is already in use
lsof -i :8080
netstat -tuln | grep 8080
```

**Solution**: Change port in `docker-compose.yml` or stop conflicting service

#### 5. Ollama Not Working

```bash
# Check if ollama service is running
docker-compose --profile with-ollama ps

# Pull a model
docker-compose exec ollama ollama pull llama3.1

# List models
docker-compose exec ollama ollama list
```

### Reset Everything

```bash
# Stop and remove everything
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

---

## 🚀 Production Deployment

### Best Practices

#### 1. Use Environment Files

```bash
# Create production env file
cp .env.docker .env.production

# Use in deployment
docker-compose --env-file .env.production up -d
```

#### 2. Enable HTTPS with Reverse Proxy

Example with Nginx:

```nginx
server {
    listen 443 ssl;
    server_name dzp.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 3. Resource Limits

Add to `docker-compose.yml`:

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

#### 4. Health Checks and Monitoring

```bash
# Check health status
docker inspect dzp-web | grep -A 10 Health

# Set up monitoring with Prometheus
# See: docs/monitoring.md
```

#### 5. Automated Backups

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker run --rm \
  -v dzp_web-sessions:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/sessions-$DATE.tar.gz -C /data .
EOF

chmod +x backup.sh

# Add to cron
0 2 * * * /path/to/backup.sh
```

#### 6. Logging

Configure logging driver:

```yaml
services:
  web:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Security

#### 1. Don't Expose Unnecessary Ports

```yaml
# Only expose web interface publicly
ports:
  - "127.0.0.1:8000:8000"  # API only on localhost
  - "0.0.0.0:8080:8080"     # Web publicly
```

#### 2. Use Secrets for API Keys

```yaml
secrets:
  openai_api_key:
    file: ./secrets/openai_key.txt

services:
  web:
    secrets:
      - openai_api_key
```

#### 3. Run as Non-Root User

Add to Dockerfile:

```dockerfile
RUN useradd -m -u 1000 dzpuser
USER dzpuser
```

---

## 📊 Useful Commands

### Development

```bash
# Build without cache
docker-compose build --no-cache

# Rebuild single service
docker-compose build web

# View resource usage
docker stats

# Shell into container
docker-compose exec web bash
docker-compose exec api bash

# Run one-off command
docker-compose run --rm web terraform version
```

### Maintenance

```bash
# Update images
docker-compose pull

# Restart services
docker-compose restart

# View logs from specific time
docker-compose logs --since 2h web

# Clean up unused resources
docker system prune -a
```

### Production

```bash
# Start in production mode
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale services
docker-compose up -d --scale web=3

# Update running service
docker-compose up -d --no-deps --build web
```

---

## 📖 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [DZP IAC Agent Documentation](./README.md)
- [API Documentation](./docs/API_DOCUMENTATION.md)
- [Web Interface Guide](./web_interface/README.md)

---

## 🆘 Getting Help

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. View logs: `docker-compose logs -f`
3. Check health: `docker-compose ps`
4. Open an issue on GitHub
5. Join our community Discord

---

**Happy Deploying! 🐳🚀**

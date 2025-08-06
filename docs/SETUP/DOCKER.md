# 🐳 Docker Setup Guide

Complete guide for setting up and managing TutorBot with Docker.

## 🎯 Overview

This guide covers Docker configuration, deployment, and management for the TutorBot application. Docker provides a consistent environment across development and production.

## 📋 Prerequisites

Before setting up Docker, ensure you have:
- Docker Engine installed
- Docker Compose installed
- Git repository cloned
- Environment variables configured

## 🚀 Quick Setup

### 1. Build and Start
```bash
# Build and start the application
docker-compose up --build -d

# View logs
docker-compose logs -f tutorbot

# Check status
docker-compose ps
```

### 2. Stop Application
```bash
# Stop the application
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## 🔧 Docker Configuration

### Dockerfile
Located at `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "main.py"]
```

### Docker Compose
Located at `docker-compose.yml`:
```yaml
version: '3.8'
services:
  tutorbot:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    volumes:
      - .:/app
    restart: unless-stopped
```

## 🎯 Docker Commands

### Basic Commands
```bash
# Build and start
docker-compose up --build

# Start in background
docker-compose up -d

# Stop application
docker-compose down

# View logs
docker-compose logs -f tutorbot

# Restart application
docker-compose restart tutorbot
```

### Development Commands
```bash
# Build without cache
docker-compose build --no-cache

# Run with specific environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Execute commands in container
docker-compose exec tutorbot python main.py
docker-compose exec tutorbot bash
```

### Debugging Commands
```bash
# View container status
docker-compose ps

# View resource usage
docker stats

# Inspect container
docker-compose exec tutorbot env
docker-compose exec tutorbot cat /app/main.py
```

## 🔧 Configuration Management

### Environment Variables
The application uses environment variables from `.env` file:
```bash
# Export environment variables
source scripts/dev/export_env.sh

# Or use Docker Compose env_file
docker-compose --env-file .env up
```

### Volume Mounts
The application mounts the current directory to `/app` in the container:
```yaml
volumes:
  - .:/app
```

This allows for:
- Live code changes without rebuilding
- Access to configuration files
- Persistent data storage

## 🎯 Docker Best Practices

### Security
- Use specific base image versions
- Run as non-root user when possible
- Minimize installed packages
- Use multi-stage builds for production

### Performance
- Use `.dockerignore` to exclude unnecessary files
- Optimize layer caching
- Use appropriate base images
- Minimize image size

### Development
- Use volume mounts for live development
- Separate development and production configs
- Use Docker Compose for multi-service setups
- Implement health checks

## 🔍 Troubleshooting

### Common Issues

#### Container Won't Start
```bash
# Check logs
docker-compose logs tutorbot

# Check container status
docker-compose ps

# Verify environment variables
docker-compose exec tutorbot env
```

#### Port Already in Use
```bash
# Check what's using the port
sudo netstat -tulpn | grep :5000

# Use different port
docker-compose up -p 5001:5000
```

#### Permission Issues
```bash
# Fix file permissions
chmod -R 755 .

# Run as specific user
docker-compose exec -u 1000:1000 tutorbot bash
```

#### Build Failures
```bash
# Clean build
docker-compose build --no-cache

# Check Dockerfile syntax
docker build -t test .

# Verify requirements.txt
docker-compose exec tutorbot pip list
```

## 📋 Docker Health Checks

### Application Health
The application should respond to health checks:
```bash
# Test application health
curl http://localhost:5000/health

# Check container health
docker-compose ps
```

### Database Connectivity
If using external databases:
```bash
# Test database connection
docker-compose exec tutorbot python -c "import requests; print('DB OK')"
```

## 🚀 Production Deployment

### Production Dockerfile
For production, consider using a multi-stage build:
```dockerfile
# Build stage
FROM python:3.9-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Production stage
FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 5000
CMD ["python", "main.py"]
```

### Production Docker Compose
```yaml
version: '3.8'
services:
  tutorbot:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 🔄 Environment Management

### Development Environment
```bash
# Development setup
FLASK_ENV=development
DEBUG_MODE=console

# Start with debug
docker-compose up --build
```

### Production Environment
```bash
# Production setup
FLASK_ENV=production
DEBUG_MODE=disabled

# Start with restart policy
docker-compose up -d --restart unless-stopped
```

### Environment-Specific Configs
```bash
# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

## 🧪 Testing with Docker

### Run Tests in Container
```bash
# Run test suite
docker-compose exec tutorbot python run_tests.py

# Run specific tests
docker-compose exec tutorbot python run_tests.py --category core

# Run with verbose output
docker-compose exec tutorbot python run_tests.py --verbose
```

### Debug Testing
```bash
# Enable debug mode
docker-compose exec tutorbot ./scripts/debug_toggle.sh on

# Run tests with debug
docker-compose exec tutorbot python run_tests.py

# Check debug logs
docker-compose logs -f tutorbot
```

## 📚 Related Documentation

- **[Environment Setup](ENVIRONMENT.md)** - Environment configuration
- **[Quick Start Guide](QUICK_START.md)** - Quick setup instructions
- **[Troubleshooting](../DEPLOYMENT/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Monitoring](../DEPLOYMENT/MONITORING.md)** - System monitoring

## 🔄 Maintenance

### Regular Tasks
- [ ] Update base images monthly
- [ ] Review security vulnerabilities quarterly
- [ ] Clean up unused images weekly
- [ ] Monitor resource usage daily
- [ ] Test backup and restore procedures monthly

### Cleanup Commands
```bash
# Remove unused containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Remove everything unused
docker system prune -a
```

### Backup and Restore
```bash
# Backup container data
docker-compose exec tutorbot tar -czf backup.tar.gz /app/data

# Restore from backup
docker-compose exec tutorbot tar -xzf backup.tar.gz -C /app
```

---

**Last Updated**: August 2025  
**Version**: 2.0  
**Maintainer**: Stephen Adei 
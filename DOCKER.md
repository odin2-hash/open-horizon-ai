# Open Horizon AI - Docker Guide

Complete guide for running Open Horizon AI using Docker and Docker Compose.

## 🚀 Quick Start

### 1. Prerequisites
- Docker and Docker Compose installed
- OpenAI API key

### 2. Basic Setup
```bash
# Clone the repository
git clone https://github.com/odin2-hash/open-horizon-ai.git
cd open-horizon-ai

# Configure environment
cp .env.example .env
# Edit .env and set your LLM_API_KEY

# Start with the helper script
./docker-start.sh
```

### 3. Access Your Application
- **API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs

## 📦 Docker Compose Configurations

### Basic Configuration (API Only)
```bash
# Start just the API service
docker-compose up

# Or with the helper script
./docker-start.sh
```

### With Nginx Reverse Proxy
```bash
# Start with nginx
docker-compose --profile with-nginx up

# Or with the helper script
./docker-start.sh --with-nginx
```
**Access**: http://localhost:80

### With Local PostgreSQL Database
```bash
# Start with local database
docker-compose --profile with-postgres up

# Or with the helper script  
./docker-start.sh --with-postgres
```
**Database**: localhost:5432

### Full Stack (API + Nginx + PostgreSQL)
```bash
# Start everything
docker-compose --profile with-nginx --profile with-postgres up

# Or with the helper script
./docker-start.sh --with-nginx --with-postgres
```

## 🔧 Configuration Options

### Environment Variables
```env
# Required
LLM_API_KEY=sk-your-openai-api-key

# Optional (defaults provided)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SECRET_KEY=your-secret-key

# App Configuration
APP_ENV=docker
DEBUG=false
LOG_LEVEL=INFO
```

### Development Mode
The `docker-compose.override.yml` automatically enables:
- Debug logging
- Live code reloading
- Volume mounting for development

To disable development features in production:
```bash
docker-compose -f docker-compose.yml up
```

## 🛠️ Available Services

### open-horizon-ai (Main Application)
- **Port**: 8000
- **Health Check**: http://localhost:8000/health
- **Endpoints**: All API endpoints available
- **Logs**: `docker-compose logs open-horizon-ai`

### nginx (Reverse Proxy)
- **Port**: 80
- **Profile**: `with-nginx`
- **Features**: Rate limiting, compression, security headers
- **Config**: `nginx.conf`

### postgres (Local Database)
- **Port**: 5432 (5433 in dev mode)
- **Profile**: `with-postgres`
- **Database**: `open_horizon_ai`
- **User/Pass**: `postgres/postgres` (dev), configurable via env

## 📋 Management Commands

### Service Management
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### Application Commands
```bash
# Run CLI inside container
docker-compose exec open-horizon-ai python cli.py

# Run tests
docker-compose exec open-horizon-ai python -m pytest

# Access shell
docker-compose exec open-horizon-ai bash

# View application logs only
docker-compose logs -f open-horizon-ai
```

### Database Management (if using postgres profile)
```bash
# Access PostgreSQL shell
docker-compose exec postgres psql -U postgres -d open_horizon_ai

# Backup database
docker-compose exec postgres pg_dump -U postgres open_horizon_ai > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T postgres psql -U postgres -d open_horizon_ai
```

## 🔧 Customization

### Custom Configuration
Create a `docker-compose.prod.yml` for production:
```yaml
version: '3.8'
services:
  open-horizon-ai:
    environment:
      - APP_ENV=production
      - DEBUG=false
      - LOG_LEVEL=WARNING
    restart: always
```

Use with: `docker-compose -f docker-compose.yml -f docker-compose.prod.yml up`

### Build Custom Image
```bash
# Build image locally
docker-compose build

# Build with no cache
docker-compose build --no-cache

# Build specific service
docker-compose build open-horizon-ai
```

### Volume Configuration
```yaml
# Add to docker-compose.yml under volumes:
services:
  open-horizon-ai:
    volumes:
      - ./custom-config:/app/config
      - ./persistent-logs:/app/logs
      - ./uploads:/app/uploads
```

## 🚨 Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Check what's using port 8000
lsof -i :8000

# Use different port
docker-compose -e PORT=8001 up
```

**2. Permission Errors**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Or run with different user
docker-compose run --user $(id -u):$(id -g) open-horizon-ai python cli.py
```

**3. Environment Variables Not Loading**
```bash
# Verify .env file exists and is readable
cat .env

# Check environment in container
docker-compose exec open-horizon-ai env | grep LLM_API_KEY
```

**4. Database Connection Issues**
```bash
# Check postgres is running (if using local db)
docker-compose exec postgres pg_isready -U postgres

# Check connection from app
docker-compose exec open-horizon-ai python -c "from dependencies import OpenHorizonDependencies; print('DB OK')"
```

**5. API Key Issues**
```bash
# Test OpenAI API key
docker-compose exec open-horizon-ai python -c "
import openai
from settings import load_settings
settings = load_settings()
client = openai.OpenAI(api_key=settings.llm_api_key)
print('API Key valid:', bool(client.models.list()))
"
```

### Health Checks
```bash
# Check container health
docker-compose ps

# Manual health check
curl http://localhost:8000/health

# Detailed health info
curl http://localhost:8000/health | jq
```

### Debugging
```bash
# Enable debug logging
docker-compose exec open-horizon-ai python -c "
import os
os.environ['LOG_LEVEL'] = 'DEBUG'
"

# View real-time logs with timestamps
docker-compose logs -f --timestamps

# Container resource usage
docker stats $(docker-compose ps -q)
```

## 📊 Monitoring

### Basic Monitoring
```bash
# Service status
watch 'docker-compose ps'

# Resource usage
watch 'docker stats --no-stream $(docker-compose ps -q)'

# Application metrics
watch 'curl -s http://localhost:8000/health | jq'
```

### Log Analysis
```bash
# Search logs for errors
docker-compose logs | grep -i error

# Monitor API calls
docker-compose logs nginx | grep POST

# Performance monitoring
docker-compose logs | grep -E "(slow|timeout|error)"
```

## 🔄 Updates & Maintenance

### Application Updates
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Maintenance
```bash
# Cleanup old data (if using postgres)
docker-compose exec postgres psql -U postgres -d open_horizon_ai -c "
SELECT cleanup_old_sessions();
"
```

### System Cleanup
```bash
# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Complete cleanup (careful!)
docker system prune -a
```

## 🚀 Production Deployment

### Production Checklist
- [ ] Set strong `SECRET_KEY` in production
- [ ] Use production database (Supabase recommended)
- [ ] Enable HTTPS with SSL certificates
- [ ] Set up proper monitoring and logging
- [ ] Configure backup strategies
- [ ] Set resource limits in compose file
- [ ] Use docker-compose production overrides
- [ ] Set up log rotation
- [ ] Configure firewall rules
- [ ] Set up automated health checks

### Production Override Example
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  open-horizon-ai:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
    environment:
      - APP_ENV=production
      - DEBUG=false
      - LOG_LEVEL=INFO
    restart: always
    
  nginx:
    ports:
      - "443:443"
    volumes:
      - ./ssl:/etc/nginx/ssl:ro
```

---

**Docker deployment makes Open Horizon AI easy to run anywhere!** 🐳
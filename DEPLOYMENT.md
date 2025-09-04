# Open Horizon AI - Deployment Guide

Complete deployment guide for the Open Horizon AI system in production environments.

## 🚀 Quick Start (Local Development)

### 1. Environment Setup
```bash
# Clone and navigate
cd agents/open_horizon_ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

### 3. Run Options
```bash
# CLI Interface (Interactive)
python cli.py

# API Server (Production)
python api.py
# or: uvicorn api:app --host 0.0.0.0 --port 8000

# Test the system
python tests/run_tests.py
```

## 🏢 Production Deployment

### Prerequisites
- Python 3.10+
- OpenAI API account with API key
- Supabase project (recommended) or PostgreSQL database
- Domain name and SSL certificate (for web deployment)
- Reverse proxy setup (nginx recommended)

### Option 1: Docker Deployment (Recommended)

**1. Create Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN groupadd -r app && useradd -r -g app app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

**2. Create docker-compose.yml:**
```yaml
version: '3.8'

services:
  open-horizon-ai:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LLM_API_KEY=${LLM_API_KEY}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - SECRET_KEY=${SECRET_KEY}
      - APP_ENV=production
      - DEBUG=false
    env_file:
      - .env
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - open-horizon-ai
    restart: unless-stopped
```

**3. Deploy:**
```bash
# Build and start
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Option 2: Server Deployment (Ubuntu/Debian)

**1. System Setup:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.11 python3.11-venv python3-pip nginx git -y

# Create application user
sudo useradd -m -s /bin/bash openhorizon
sudo mkdir -p /opt/open-horizon-ai
sudo chown openhorizon:openhorizon /opt/open-horizon-ai
```

**2. Application Setup:**
```bash
# Switch to application user
sudo su - openhorizon

# Clone/copy application
cd /opt/open-horizon-ai
# Copy your application files here

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Configure environment
cp .env.example .env
# Edit .env with production values
```

**3. Create Systemd Service:**
```bash
# Create service file
sudo nano /etc/systemd/system/open-horizon-ai.service
```

```ini
[Unit]
Description=Open Horizon AI API
After=network.target

[Service]
Type=exec
User=openhorizon
Group=openhorizon
WorkingDirectory=/opt/open-horizon-ai
Environment=PATH=/opt/open-horizon-ai/venv/bin
ExecStart=/opt/open-horizon-ai/venv/bin/gunicorn --bind 127.0.0.1:8000 api:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**4. Start Services:**
```bash
# Enable and start application
sudo systemctl enable open-horizon-ai
sudo systemctl start open-horizon-ai
sudo systemctl status open-horizon-ai

# Configure nginx
sudo nano /etc/nginx/sites-available/open-horizon-ai
```

**5. Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

**6. Enable Site:**
```bash
sudo ln -s /etc/nginx/sites-available/open-horizon-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔧 Configuration Management

### Environment Variables (Production)

```bash
# Required - LLM Configuration
LLM_PROVIDER=openai
LLM_API_KEY=sk-prod-your-key-here
LLM_MODEL=gpt-4o-mini
LLM_BASE_URL=https://api.openai.com/v1

# Required - Database
SUPABASE_URL=https://prod-project.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Required - Security
SECRET_KEY=production-secret-key-256-bits-long
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Application Settings
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO
MAX_RETRIES=3
TIMEOUT_SECONDS=30

# Performance
DATABASE_POOL_SIZE=20
DATABASE_MAX_CONNECTIONS=50

# CORS (for frontend)
ALLOWED_ORIGINS=https://your-frontend-domain.com
CORS_ALLOW_CREDENTIALS=true

# Optional - External APIs
ERASMUS_PARTNER_DB_API_KEY=your-partner-api-key
```

### Security Checklist

- [ ] **API Keys**: Stored in environment variables, never in code
- [ ] **HTTPS**: SSL certificate properly configured
- [ ] **CORS**: Restricted to your frontend domain(s)
- [ ] **JWT Secret**: Strong, random, and unique per environment
- [ ] **Database**: Service key restricted to necessary operations
- [ ] **Firewall**: Only necessary ports (80, 443, 22) open
- [ ] **Updates**: System and dependencies regularly updated
- [ ] **Backups**: Database and configuration files backed up
- [ ] **Logging**: Application logs monitored and rotated
- [ ] **Health Checks**: Monitoring endpoints configured

## 📊 Monitoring & Maintenance

### Health Monitoring

**1. Built-in Health Endpoints:**
```bash
# Basic health check
curl https://your-domain.com/health

# Detailed status
curl https://your-domain.com/api/health-detailed
```

**2. Log Monitoring:**
```bash
# Application logs
sudo journalctl -u open-horizon-ai -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

**3. System Resource Monitoring:**
```bash
# CPU and memory usage
htop
free -h
df -h

# Application-specific
ps aux | grep gunicorn
netstat -tulpn | grep 8000
```

### Backup Strategy

**1. Database Backups (if using PostgreSQL):**
```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h your-db-host -U username dbname > backup_$DATE.sql
aws s3 cp backup_$DATE.sql s3://your-backup-bucket/
```

**2. Configuration Backups:**
```bash
# Environment and configuration files
tar -czf config_backup_$(date +%Y%m%d).tar.gz .env nginx.conf docker-compose.yml
```

### Performance Optimization

**1. Gunicorn Configuration:**
```bash
# Optimize worker count (CPU cores * 2 + 1)
--workers 9  # for 4-core server
--worker-connections 1000
--max-requests 1000
--max-requests-jitter 100
--preload-app
```

**2. Nginx Optimization:**
```nginx
# Add to nginx config
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

client_max_body_size 50M;
keepalive_timeout 65;
```

## 🔄 Updates & Maintenance

### Application Updates

**1. Zero-downtime deployment:**
```bash
# Pull new version
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Run tests
python tests/run_tests.py

# Graceful restart
sudo systemctl reload open-horizon-ai
```

**2. Database Migrations:**
```bash
# If using custom migrations
python migrate.py

# Supabase migrations are automatic
```

### Backup & Restore Procedures

**1. Create Backup:**
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p backups/$DATE

# Database backup (if applicable)
# pg_dump ... > backups/$DATE/database.sql

# Configuration backup
cp .env backups/$DATE/
cp docker-compose.yml backups/$DATE/
cp -r nginx/ backups/$DATE/

# Compress
tar -czf backups/open_horizon_backup_$DATE.tar.gz backups/$DATE/
```

**2. Restore from Backup:**
```bash
#!/bin/bash
# restore.sh BACKUP_DATE
BACKUP_DATE=$1
tar -xzf backups/open_horizon_backup_$BACKUP_DATE.tar.gz
cp backups/$BACKUP_DATE/.env .
# Restore other configurations as needed
```

## 🌍 Swedish NGO Specific Setup

### Open Horizon Integration

**1. Organization Branding:**
```bash
# Update organization context in settings
export ORG_NAME="Open Horizon"
export ORG_COUNTRY="Sweden"
export DEFAULT_LANGUAGE="en"
```

**2. Swedish National Agency Integration:**
```bash
# MUCF (Youth) and UHR (Education) endpoints
export SWEDISH_NA_MUCF_URL="https://api.mucf.se"
export SWEDISH_NA_UHR_URL="https://api.uhr.se"
```

### Compliance Features

**1. GDPR Compliance:**
- Data retention policies configured
- User consent management
- Data export capabilities
- Right to erasure functionality

**2. Erasmus+ Programme Compliance:**
- Latest Programme Guide integrated
- Swedish National Agency guidelines
- Currency conversion (EUR ↔ SEK)
- Deadline tracking for Swedish submissions

## 🚨 Troubleshooting

### Common Issues

**1. "Agent execution failed" errors:**
```bash
# Check API key
curl -H "Authorization: Bearer $LLM_API_KEY" https://api.openai.com/v1/models

# Check logs
docker-compose logs open-horizon-ai

# Verify environment
python -c "from settings import load_settings; print(load_settings())"
```

**2. Database connection issues:**
```bash
# Test Supabase connection
python -c "from supabase import create_client; client = create_client('URL', 'KEY'); print(client.table('test').select('*').execute())"
```

**3. High memory usage:**
```bash
# Reduce worker count
# Update docker-compose.yml or systemd service
# Monitor with: docker stats
```

### Emergency Procedures

**1. Service Recovery:**
```bash
# Quick restart
docker-compose restart

# Or for systemd
sudo systemctl restart open-horizon-ai nginx

# Check status
docker-compose ps
sudo systemctl status open-horizon-ai
```

**2. Rollback Procedure:**
```bash
# Switch to previous version
git checkout previous-stable-tag
docker-compose down
docker-compose up -d --build
```

## 📞 Support & Maintenance Contacts

- **Technical Issues**: [Your tech support contact]
- **OpenAI API Issues**: https://platform.openai.com/support
- **Supabase Support**: https://supabase.com/support
- **Erasmus+ Programme Questions**: Swedish National Agencies (MUCF/UHR)

---

**Production Deployment Checklist:**
- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Health checks passing
- [ ] Monitoring configured
- [ ] Backups automated
- [ ] Security hardening complete
- [ ] Performance optimization applied
- [ ] Documentation updated
- [ ] Staff training completed

**Open Horizon AI** is ready for production deployment! 🚀
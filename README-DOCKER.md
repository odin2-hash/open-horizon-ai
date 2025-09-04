# 🐳 Open Horizon AI - Docker Quick Start

Run Open Horizon AI without cloning the repository! Just download the docker-compose file and start.

## Quick Start (No Repository Clone Needed)

### 1. Download and Run
```bash
# Download the standalone docker-compose file
curl -O https://raw.githubusercontent.com/odin2-hash/open-horizon-ai/main/docker-compose.standalone.yml

# Download environment template
curl -O https://raw.githubusercontent.com/odin2-hash/open-horizon-ai/main/.env.example

# Copy and configure environment
cp .env.example .env
# Edit .env with your API keys and configuration

# Start the application
docker-compose -f docker-compose.standalone.yml up -d
```

### 2. Access the Application
- **Frontend**: http://localhost:3030
- **Backend API**: http://localhost:8090
- **API Documentation**: http://localhost:8090/docs

## Environment Configuration

Before starting, you **must** configure your `.env` file with:

### Required Configuration
```bash
# LLM Configuration
LLM_API_KEY=your_openai_api_key_here

# Supabase Configuration  
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# Erasmus+ Integration
ERASMUS_PARTNER_DB_API_KEY=your_erasmus_partner_db_key

# Security
SECRET_KEY=your-secure-random-secret-key-here
```

## Optional Profiles

### With Nginx Reverse Proxy
```bash
docker-compose -f docker-compose.standalone.yml --profile with-nginx up -d
```
Access via: http://localhost (port 80)

### With Local PostgreSQL
```bash
# Set POSTGRES_PASSWORD in .env first
docker-compose -f docker-compose.standalone.yml --profile with-postgres up -d
```

## Management Commands

```bash
# Start services
docker-compose -f docker-compose.standalone.yml up -d

# Stop services
docker-compose -f docker-compose.standalone.yml down

# View logs
docker-compose -f docker-compose.standalone.yml logs -f

# Update to latest images
docker-compose -f docker-compose.standalone.yml pull
docker-compose -f docker-compose.standalone.yml up -d
```

## Health Checks

The backend includes health checks available at:
- `http://localhost:8090/health` - Basic health check
- `http://localhost:8090/api/health` - API health check

## Troubleshooting

### Port Conflicts
If you have port conflicts, modify the docker-compose.standalone.yml:
```yaml
ports:
  - "YOUR_PORT:3030"  # Frontend
  - "YOUR_PORT:8090"  # Backend
```

### View Container Status
```bash
docker-compose -f docker-compose.standalone.yml ps
```

### Reset Everything
```bash
docker-compose -f docker-compose.standalone.yml down -v
docker-compose -f docker-compose.standalone.yml up -d
```

## Image Information

Images are automatically built and published to GitHub Container Registry:
- **Backend**: `ghcr.io/odin2-hash/open-horizon-ai-backend:latest`
- **Frontend**: `ghcr.io/odin2-hash/open-horizon-ai-frontend:latest`

## Development Mode

For development with live code changes, clone the repository and use:
```bash
git clone https://github.com/odin2-hash/open-horizon-ai.git
cd open-horizon-ai
docker-compose up -d
```
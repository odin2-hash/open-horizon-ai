#!/bin/bash

# Open Horizon AI Docker Startup Script

set -e

echo "🚀 Starting Open Horizon AI with Docker Compose..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys before continuing."
    echo "Required: LLM_API_KEY (OpenAI API key)"
    echo "Optional: SUPABASE_URL, SUPABASE_KEY (for data persistence)"
    exit 1
fi

# Check if OpenAI API key is set
if grep -q "sk-your-openai-api-key-here" .env; then
    echo "❌ Please set your OpenAI API key in .env file"
    echo "Edit LLM_API_KEY=sk-your-actual-openai-key"
    exit 1
fi

# Create logs directory
mkdir -p logs

# Parse command line arguments
PROFILE=""
BUILD_FLAG=""
DETACH_FLAG=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --with-nginx)
            PROFILE="--profile with-nginx"
            echo "🌐 Including nginx reverse proxy"
            shift
            ;;
        --with-postgres)
            PROFILE="$PROFILE --profile with-postgres"
            echo "🐘 Including PostgreSQL database"
            shift
            ;;
        --build)
            BUILD_FLAG="--build"
            echo "🔨 Building images"
            shift
            ;;
        --detach|-d)
            DETACH_FLAG="-d"
            shift
            ;;
        --help|-h)
            echo "Open Horizon AI Docker Startup Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --with-nginx     Include nginx reverse proxy"
            echo "  --with-postgres  Include PostgreSQL database"
            echo "  --build          Build images before starting"
            echo "  --detach, -d     Run in background"
            echo "  --help, -h       Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                           # Basic setup with just the API"
            echo "  $0 --with-nginx             # With nginx reverse proxy"
            echo "  $0 --with-nginx --with-postgres  # Full stack with database"
            echo "  $0 --build -d               # Build and run in background"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Start services
echo "📦 Starting Docker services..."
if [ -n "$PROFILE" ]; then
    echo "Using profiles:$PROFILE"
fi

docker-compose up $PROFILE $BUILD_FLAG $DETACH_FLAG

# If running in detached mode, show status
if [ "$DETACH_FLAG" = "-d" ]; then
    echo ""
    echo "✅ Services started in background!"
    echo ""
    echo "📊 Service Status:"
    docker-compose ps
    echo ""
    echo "🌐 Access points:"
    echo "  - API: http://localhost:8000"
    echo "  - Health: http://localhost:8000/health"
    if [[ $PROFILE == *"with-nginx"* ]]; then
        echo "  - Nginx: http://localhost:80"
    fi
    echo ""
    echo "📋 Useful commands:"
    echo "  docker-compose logs -f              # View logs"
    echo "  docker-compose ps                   # Service status"
    echo "  docker-compose down                 # Stop services"
    echo "  docker-compose exec open-horizon-ai python cli.py  # Run CLI inside container"
fi
#!/bin/bash
# YGG Torrent API Docker Run Script

set -e

echo "🐳 YGG Torrent API Docker Setup"
echo "================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data logs

# Build and start the container
echo "🔨 Building Docker image..."
docker-compose build

echo "🚀 Starting YGG Torrent API..."
docker-compose up -d

# Wait for the service to be ready
echo "⏳ Waiting for API to be ready..."
sleep 10

# Check if the API is running
echo "🔍 Checking API health..."
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ API is running successfully!"
    echo ""
    echo "🌐 API Endpoints:"
    echo "   Health: http://localhost:8080/health"
    echo "   Auth:   http://localhost:8080/auth/login"
    echo "   Categories: http://localhost:8080/categories"
    echo ""
    echo "📖 Usage:"
    echo "   curl -X POST http://localhost:8080/auth/login \\"
    echo "     -H 'Content-Type: application/json' \\"
    echo "     -d '{\"username\":\"your_username\",\"password\":\"your_password\"}'"
    echo ""
    echo "🛑 To stop: docker-compose down"
    echo "📊 To view logs: docker-compose logs -f"
else
    echo "❌ API failed to start. Check logs with: docker-compose logs"
    exit 1
fi

#!/bin/bash
# Test Docker Configuration Script

echo "🐳 YGG Torrent API Docker Configuration Test"
echo "============================================="

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "✅ Docker is installed: $(docker --version)"
else
    echo "⚠️  Docker is not installed. Please install Docker to test the container."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is available
if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose is installed: $(docker-compose --version)"
else
    echo "⚠️  Docker Compose is not installed. Please install Docker Compose."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Validate Dockerfile syntax
echo ""
echo "🔍 Validating Dockerfile..."
if docker build --dry-run . > /dev/null 2>&1; then
    echo "✅ Dockerfile syntax is valid"
else
    echo "❌ Dockerfile has syntax errors"
    exit 1
fi

# Validate docker-compose.yml
echo ""
echo "🔍 Validating docker-compose.yml..."
if docker-compose config > /dev/null 2>&1; then
    echo "✅ docker-compose.yml is valid"
else
    echo "❌ docker-compose.yml has syntax errors"
    exit 1
fi

# Check required files
echo ""
echo "🔍 Checking required files..."
required_files=(
    "Dockerfile"
    "docker-compose.yml"
    "docker.env"
    "requirements_api.txt"
    "ygg_api.py"
    ".dockerignore"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file is missing"
        exit 1
    fi
done

# Test build (dry run)
echo ""
echo "🔨 Testing Docker build (dry run)..."
if docker build --dry-run . > /dev/null 2>&1; then
    echo "✅ Docker build configuration is valid"
else
    echo "❌ Docker build failed"
    exit 1
fi

echo ""
echo "🎉 All Docker configuration tests passed!"
echo ""
echo "📋 Next steps:"
echo "   1. Run: docker-compose build"
echo "   2. Run: docker-compose up -d"
echo "   3. Test: curl http://localhost:8080/health"
echo ""
echo "📖 For detailed instructions, see DOCKER_README.md"

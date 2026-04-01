#!/bin/bash
# Deploy script for production deployment

set -e

APP_NAME="luxury-rideshare-agent"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-docker.io}"
DOCKER_IMAGE="${DOCKER_REGISTRY}/blueroyalrides13/${APP_NAME}"
VERSION="${VERSION:-latest}"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║    Luxury Ride Share Agent - Production Deploy             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Build Docker image
echo "🏗️  Building Docker image..."
docker build -t "${DOCKER_IMAGE}:${VERSION}" .
echo "✓ Docker image built: ${DOCKER_IMAGE}:${VERSION}"

# Push to registry (optional)
if [ "$PUSH_REGISTRY" = "true" ]; then
    echo ""
    echo "📤 Pushing to Docker registry..."
    docker push "${DOCKER_IMAGE}:${VERSION}"
    echo "✓ Image pushed to registry"
fi

# Deploy with Docker Compose
echo ""
echo "🚀 Deploying with Docker Compose..."
docker-compose up -d
echo "✓ Services started"

# Wait for health check
echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ API is healthy"
else
    echo "✗ API health check failed"
    echo "Run 'docker-compose logs app' to see error details"
    exit 1
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║            Deployment Successful! ✓                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "API is running at: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""

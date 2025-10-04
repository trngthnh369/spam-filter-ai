#!/bin/bash

set -e

echo "========================================="
echo "Spam Filter AI - Deployment Script"
echo "========================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed"
    exit 1
fi

# Check if artifacts exist
if [ ! -f "artifacts/faiss_index.bin" ]; then
    echo "Error: Model artifacts not found"
    echo "Please run training pipeline first: make train"
    exit 1
fi

echo ""
echo "[1/5] Stopping existing services..."
docker-compose down

echo ""
echo "[2/5] Building Docker images..."
docker-compose build

echo ""
echo "[3/5] Starting services..."
docker-compose up -d

echo ""
echo "[4/5] Waiting for services to be healthy..."
sleep 10

# Health check
echo ""
echo "[5/5] Checking service health..."
backend_health=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health)

if [ "$backend_health" = "200" ]; then
    echo "✓ Backend is healthy"
else
    echo "✗ Backend health check failed (HTTP $backend_health)"
    docker-compose logs backend
    exit 1
fi

echo ""
echo "========================================="
echo "✓ Deployment successful!"
echo "========================================="
echo ""
echo "Services:"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs:    http://localhost:8000/docs"
echo "  - Frontend:    http://localhost:3000"
echo ""
echo "Commands:"
echo "  - View logs:   docker-compose logs -f"
echo "  - Stop:        docker-compose down"
echo "  - Restart:     docker-compose restart"
echo ""
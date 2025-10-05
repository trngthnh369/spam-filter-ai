#!/bin/bash

set -e

echo "========================================="
echo "Spam Filter AI - Deployment Script"
echo "========================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_error() {
    echo -e "${RED}❌ Error: $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ Warning: $1${NC}"
}

print_info() {
    echo "ℹ $1"
}

# Check if Docker is installed
echo "[1/8] Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi
print_success "Docker is installed: $(docker --version)"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi
print_success "Docker Compose is installed"

# Check if Docker daemon is running
echo ""
echo "[2/8] Checking Docker daemon..."
if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running"
    echo "Please start Docker Desktop or Docker service"
    exit 1
fi
print_success "Docker daemon is running"

# Validate artifacts directory exists
echo ""
echo "[3/8] Validating model artifacts..."
if [ ! -d "artifacts" ]; then
    print_error "artifacts/ directory not found"
    echo "Please run the training pipeline first:"
    echo "  cd backend && source venv/bin/activate"
    echo "  cd ../scripts && python run_pipeline.py"
    exit 1
fi

# Check for required artifact files
REQUIRED_FILES=(
    "artifacts/faiss_index.bin"
    "artifacts/train_metadata.json"
    "artifacts/class_weights.json"
    "artifacts/model_config.json"
)

MISSING_FILES=()
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    print_error "Required artifact files are missing:"
    for file in "${MISSING_FILES[@]}"; do
        echo "  - $file"
    done
    echo ""
    echo "Please run the training pipeline first:"
    echo "  cd backend && source venv/bin/activate"
    echo "  cd ../scripts && python run_pipeline.py"
    exit 1
fi

print_success "All required artifacts found"

# Show artifact info
if [ -f "artifacts/model_config.json" ]; then
    print_info "Model info:"
    python3 << 'PYTHON_SCRIPT'
import json
try:
    with open('artifacts/model_config.json', 'r') as f:
        config = json.load(f)
    print(f"  - Model: {config.get('model_name', 'Unknown')}")
    print(f"  - Best Alpha: {config.get('best_alpha', 'Unknown')}")
    print(f"  - Train Samples: {config.get('train_samples', 'Unknown')}")
    print(f"  - Trained: {config.get('trained_at', 'Unknown')}")
except Exception as e:
    print(f"  Could not read config: {e}")
PYTHON_SCRIPT
fi

# Stop existing services
echo ""
echo "[4/8] Stopping existing services..."
docker-compose down --remove-orphans 2>/dev/null || true
print_success "Existing services stopped"

# Clean up old images (optional)
read -p "Do you want to rebuild images from scratch? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "[5/8] Removing old images..."
    docker-compose down --rmi local 2>/dev/null || true
    print_success "Old images removed"
else
    echo ""
    echo "[5/8] Skipping image cleanup..."
fi

# Build Docker images
echo ""
echo "[6/8] Building Docker images..."
echo "This may take several minutes on first run..."
if docker-compose build --progress=plain; then
    print_success "Docker images built successfully"
else
    print_error "Failed to build Docker images"
    exit 1
fi

# Start services
echo ""
echo "[7/8] Starting services..."
if docker-compose up -d; then
    print_success "Services started"
else
    print_error "Failed to start services"
    exit 1
fi

# Wait for services to be healthy
echo ""
echo "[8/8] Waiting for services to be healthy..."
echo "This may take up to 60 seconds..."

MAX_WAIT=60
ELAPSED=0

while [ $ELAPSED -lt $MAX_WAIT ]; do
    BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health 2>/dev/null || echo "000")
    
    if [ "$BACKEND_HEALTH" = "200" ]; then
        print_success "Backend is healthy"
        break
    fi
    
    echo -n "."
    sleep 2
    ELAPSED=$((ELAPSED + 2))
done

echo ""

if [ "$BACKEND_HEALTH" != "200" ]; then
    print_warning "Backend health check failed or timed out"
    echo ""
    echo "Checking backend logs:"
    docker-compose logs --tail=20 backend
    echo ""
    print_info "You can check full logs with: docker-compose logs backend"
fi

# Check frontend
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "000")
if [ "$FRONTEND_STATUS" = "200" ] || [ "$FRONTEND_STATUS" = "304" ]; then
    print_success "Frontend is accessible"
else
    print_warning "Frontend may still be starting up"
fi

# Show running containers
echo ""
echo "Running containers:"
docker-compose ps

echo ""
echo "========================================="
echo "✓ Deployment Complete!"
echo "========================================="
echo ""
echo "Services:"
echo "  - Backend API:  http://localhost:8000"
echo "  - API Docs:     http://localhost:8000/docs"
echo "  - Frontend:     http://localhost:3000"
echo ""
echo "Useful commands:"
echo "  - View logs:        docker-compose logs -f"
echo "  - View backend:     docker-compose logs -f backend"
echo "  - View frontend:    docker-compose logs -f frontend"
echo "  - Stop services:    docker-compose down"
echo "  - Restart:          docker-compose restart"
echo "  - Quick test:       bash scripts/quick_test.sh"
echo ""
echo "If services are not responding, check logs with:"
echo "  docker-compose logs"
echo ""
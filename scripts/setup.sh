#!/bin/bash

set -e

echo "========================================="
echo "Spam Filter AI - Setup Script"
echo "========================================="
echo ""

# Check prerequisites
echo "[0/7] Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.10+ from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python version: $PYTHON_VERSION"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed"
    echo "Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node --version)
echo "✓ Node.js version: $NODE_VERSION"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is not installed"
    exit 1
fi

echo "✓ npm version: $(npm --version)"

# Create project structure
echo ""
echo "[1/7] Creating project structure..."
mkdir -p data
mkdir -p artifacts
mkdir -p scripts
mkdir -p backend/{app/{api/routes,core,services,middleware,utils},tests}
mkdir -p frontend/src/{components,pages,lib,styles}
mkdir -p frontend/public
mkdir -p logs

echo "✓ Created directory structure"

# Create .env file for backend
echo ""
echo "[2/7] Creating environment files..."

if [ ! -f "backend/.env" ]; then
    cat > backend/.env << 'EOF'
# Backend Configuration
MODEL_NAME=intfloat/multilingual-e5-base
DEFAULT_K=5
DEFAULT_ALPHA=0.8
MAX_SEQUENCE_LENGTH=512
BATCH_SIZE=32
MAX_MESSAGE_LENGTH=10000
RATE_LIMIT=100

# Paths
FAISS_INDEX_PATH=artifacts/faiss_index.bin
METADATA_PATH=artifacts/train_metadata.json
CLASS_WEIGHTS_PATH=artifacts/class_weights.json
CONFIG_PATH=artifacts/model_config.json
DATA_DIR=data

# Data Sources
ENGLISH_DATA_ID=1N7rk-kfnDFIGMeX0ROVTjKh71gcgx-7R
VIETNAMESE_DATASET=victorhoward2/vietnamese-spam-post-in-social-network

# Augmentation Parameters
AUG_RATIO=0.2
ALPHA_SPAM=0.5
ALPHA_HAM=0.3

# API Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000
LOG_LEVEL=INFO
EOF
    echo "✓ Created backend/.env file"
else
    echo "✓ backend/.env file already exists"
fi

# Create .env file for frontend
if [ ! -f "frontend/.env.local" ]; then
    cat > frontend/.env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_TELEMETRY_DISABLED=1
EOF
    echo "✓ Created frontend/.env.local file"
else
    echo "✓ frontend/.env.local file already exists"
fi

# Install Python dependencies
echo ""
echo "[3/7] Installing Python dependencies..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null

# Upgrade pip
pip install --upgrade pip --quiet

# Install requirements
echo "Installing Python packages (this may take a few minutes)..."
pip install -r requirements.txt --quiet

echo "✓ Python dependencies installed"
cd ..

# Install Node dependencies
echo ""
echo "[4/7] Installing Node.js dependencies..."
cd frontend

echo "Installing npm packages (this may take a few minutes)..."
npm install --silent

echo "✓ Node.js dependencies installed"
cd ..

# Download NLTK data
echo ""
echo "[5/7] Downloading NLTK data..."
cd backend
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null
python3 << 'PYTHON_SCRIPT'
import nltk
import sys

try:
    print("Downloading wordnet...")
    nltk.download('wordnet', quiet=True)
    print("Downloading omw-1.4...")
    nltk.download('omw-1.4', quiet=True)
    print("✓ NLTK data downloaded successfully")
except Exception as e:
    print(f"Warning: Failed to download NLTK data: {e}", file=sys.stderr)
    print("You may need to download manually later", file=sys.stderr)
PYTHON_SCRIPT
cd ..

# Create placeholder files
echo ""
echo "[6/7] Creating placeholder files..."
touch data/.gitkeep
touch artifacts/.gitkeep
touch logs/.gitkeep
echo "✓ Created placeholder files"

# Make scripts executable
echo ""
echo "[7/7] Setting script permissions..."
chmod +x scripts/*.sh
chmod +x scripts/*.py 2>/dev/null || true
echo "✓ Set script permissions"

echo ""
echo "========================================="
echo "✓ Setup complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Train the model:"
echo "   cd backend && source venv/bin/activate"
echo "   cd ../scripts && python run_pipeline.py"
echo ""
echo "2. Start development servers:"
echo "   Backend:  cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "   Frontend: cd frontend && npm run dev"
echo ""
echo "3. Or deploy with Docker (after training):"
echo "   make deploy"
echo ""
echo "For more information, see README.md"
echo ""
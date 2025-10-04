#!/bin/bash

set -e

echo "========================================="
echo "Spam Filter AI - Setup Script"
echo "========================================="

# Create directories
echo ""
echo "[1/5] Creating project structure..."
mkdir -p data artifacts notebooks/outputs backend/app/{api/routes,core,services} frontend/src/{components,pages,lib} tests

# Create .env file
echo ""
echo "[2/5] Creating environment file..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
# Backend Configuration
MODEL_NAME=intfloat/multilingual-e5-base
DEFAULT_K=5
DEFAULT_ALPHA=0.5
MAX_MESSAGE_LENGTH=10000

# Data Configuration
ENGLISH_DATA_ID=1N7rk-kfnDFIGMeX0ROVTjKh71gcgx-7R
VIETNAMESE_DATASET=victorhoward2/vietnamese-spam-post-in-social-network

# Augmentation
AUG_RATIO=0.2
ALPHA_SPAM=0.5
ALPHA_HAM=0.3

# API Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
    echo "✓ Created .env file"
else
    echo "✓ .env file already exists"
fi

# Install Python dependencies
echo ""
echo "[3/5] Installing Python dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install Node dependencies
echo ""
echo "[4/5] Installing Node.js dependencies..."
cd frontend
npm install
cd ..

# Download NLTK data
echo ""
echo "[5/5] Downloading NLTK data..."
python -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')"

echo ""
echo "========================================="
echo "✓ Setup complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Run training: make train"
echo "  2. Deploy:       make deploy"
echo ""
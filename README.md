# 🛡️ Spam Filter AI

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14.1-black.svg)](https://nextjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An enterprise-grade AI-powered spam detection system with explainability features, supporting English and Vietnamese languages. Built with multilingual E5 embeddings, FAISS vector search, and weighted KNN classification.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Performance Metrics](#performance-metrics)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Training the Model](#training-the-model)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Dataset Information](#dataset-information)
- [Configuration](#configuration)
- [Development](#development)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

Spam Filter AI is a production-ready spam detection system that combines state-of-the-art natural language processing with explainable AI techniques. The system achieves 95-98% accuracy while providing transparent, token-level explanations for each prediction.

### Why This Project?

- **Multilingual Support**: Seamlessly handles both English and Vietnamese text
- **Explainable Predictions**: See exactly which words influenced the classification
- **Production Ready**: Complete with Docker deployment, API documentation, and monitoring
- **High Performance**: Sub-50ms inference time with 95%+ accuracy
- **Spam Subcategorization**: Automatically categorizes spam into meaningful types

---

## 🌟 Key Features

### Core Capabilities

✅ **Multilingual Classification**
- English and Vietnamese language support
- Unified multilingual E5 embeddings (768 dimensions)
- No language-specific preprocessing required

✅ **High Accuracy Detection**
- 95-98% overall accuracy
- Optimized weighted KNN classifier
- Smart handling of class imbalance

✅ **Explainable AI**
- Token-level saliency analysis
- Identifies key spam indicators
- Shows similar training examples

✅ **Spam Subcategorization**
- Advertising spam detection
- System/security spam detection
- Automatic categorization

✅ **Real-time Processing**
- Fast FAISS-accelerated vector search
- Batch processing support
- Sub-50ms average response time

✅ **Production API**
- RESTful FastAPI backend
- Comprehensive OpenAPI documentation
- Rate limiting and logging middleware

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js + React)                │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │ Classifier   │  │   Result     │  │  Statistics     │   │
│  │    Form      │  │   Display    │  │     Panel       │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   REST API        │
                    │   (FastAPI)       │
                    └─────────┬─────────┘
                              │
┌─────────────────────────────▼─────────────────────────────┐
│                    Backend Services                        │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Model Service                                       │ │
│  │  • Multilingual-E5 Embeddings (768-dim)            │ │
│  │  • FAISS IndexFlatIP (Cosine Similarity)           │ │
│  │  • Weighted KNN (Optimized Alpha)                  │ │
│  │  • Token Saliency (Masking-based)                  │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼─────────────────────────────┐
│                    Training Pipeline                       │
│  Data Loading → Augmentation → Training → Artifacts       │
│  • Google Drive (English dataset)                         │
│  • Kaggle (Vietnamese dataset)                            │
│  • Hard example generation                                │
│  • Synonym replacement                                    │
│  • Alpha optimization                                     │
└────────────────────────────────────────────────────────────┘
```

---

## 📊 Performance Metrics

| Metric              | Value      |
|---------------------|------------|
| Overall Accuracy    | 95-98%     |
| Precision (Spam)    | 93-96%     |
| Recall (Spam)       | 90-95%     |
| F1-Score            | 92-96%     |
| Inference Time      | <50ms      |
| Embedding Dimension | 768        |
| Supported Languages | 2 (EN, VI) |

---

## 🚀 Quick Start

### Prerequisites

Ensure you have the following installed:

- **Python 3.10+**
- **Node.js 18+**
- **Docker & Docker Compose** (for containerized deployment)
- **8GB+ RAM** (recommended for model training)

### One-Command Setup

```bash
# Clone and setup
git clone https://github.com/trngthnh369/spam-filter-ai.git
cd spam-filter-ai
bash scripts/setup.sh

# Train model
cd backend && source venv/bin/activate
cd ../scripts && python run_pipeline.py

# Deploy with Docker
cd .. && bash scripts/deploy.sh
```

**Services will be available at:**
- Backend API: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Frontend: `http://localhost:3000`

---

## 📦 Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/trngthnh369/spam-filter-ai.git
cd spam-filter-ai
```

### Step 2: Automated Setup

```bash
bash scripts/setup.sh
```

This script will:
- ✓ Verify Python and Node.js installations
- ✓ Create project directory structure
- ✓ Generate environment configuration files
- ✓ Install Python dependencies
- ✓ Install Node.js dependencies
- ✓ Download NLTK data

### Step 3: Manual Setup (Alternative)

If the automated script fails, follow these steps:

**Backend Setup:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend Setup:**
```bash
cd frontend
npm install
```

---

## 🎓 Training the Model

### Quick Training

```bash
cd backend && source venv/bin/activate
cd ../scripts
python run_pipeline.py
```

### Training Pipeline Stages

The training pipeline consists of four stages:

1. **Data Loading** (2-3 minutes)
   - Downloads English dataset from Google Drive
   - Downloads Vietnamese dataset from Kaggle
   - Combines and preprocesses data

2. **Data Augmentation** (3-5 minutes)
   - Generates hard negative examples
   - Creates synonym replacements
   - Balances class distribution

3. **Model Training** (5-10 minutes)
   - Generates multilingual E5 embeddings
   - Builds FAISS index
   - Optimizes alpha parameter
   - Validates on test set

4. **Artifact Generation**
   - Saves FAISS index (`faiss_index.bin`)
   - Saves training metadata (`train_metadata.json`)
   - Saves class weights (`class_weights.json`)
   - Saves model configuration (`model_config.json`)

### Expected Output

```
[STEP 1] Loading datasets...
✓ Loaded 5572 English samples
✓ Loaded 3000+ Vietnamese samples

[STEP 2] Augmenting data...
✓ Generated 500+ hard examples
✓ Generated 1200+ synonym replacements

[STEP 3] Training model...
✓ Optimizing alpha parameter...
✓ Best alpha: 0.8 with accuracy: 0.9650

✓ Artifacts saved to artifacts/
```

### Custom Training Options

```bash
# Skip data augmentation
python run_pipeline.py --no-augmentation

# Custom test split
python run_pipeline.py --test-size 0.3

# Custom augmentation ratio
python run_pipeline.py --aug-ratio 0.3
```

---

## 🐳 Deployment

### Docker Deployment (Recommended)

**⚠️ Important:** You must train the model before deploying with Docker.

```bash
# 1. Train the model
make train

# 2. Deploy services
make deploy

# Or use the deployment script
bash scripts/deploy.sh
```

The deployment script will:
- ✓ Validate Docker installation
- ✓ Check for required artifacts
- ✓ Build Docker images
- ✓ Start services
- ✓ Run health checks

### Manual Deployment (Development)

**Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

### Docker Compose Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend

# Restart services
docker-compose restart

# Rebuild images
docker-compose build --no-cache
```

---

## 📡 API Documentation

### Interactive API Docs

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Core Endpoints

#### 1. Single Message Classification

```bash
POST /api/v1/classify
```

**Request:**
```json
{
  "message": "Win free iPhone now!",
  "k": 5,
  "alpha": 0.8,
  "explain": true
}
```

**Response:**
```json
{
  "prediction": "spam",
  "is_spam": true,
  "confidence": 0.95,
  "vote_scores": {"ham": 0.12, "spam": 2.38},
  "subcategory": "spam_quangcao",
  "saliency_weight": 0.85,
  "neighbors": [...],
  "tokens": [
    {"token": "win", "saliency": 0.89},
    {"token": "free", "saliency": 0.92}
  ],
  "processing_time_ms": 45.2
}
```

#### 2. Batch Classification

```bash
POST /api/v1/classify/batch
```

**Request:**
```json
{
  "messages": [
    "Hello friend",
    "Click here for prize",
    "Meeting at 3pm"
  ],
  "k": 5
}
```

#### 3. Explainability Endpoint

```bash
POST /api/v1/explain
```

**Request:**
```json
{
  "message": "Congratulations! You won $1000",
  "k": 10
}
```

#### 4. Statistics

```bash
GET /api/v1/stats
```

#### 5. Health Check

```bash
GET /api/v1/health
```

---

## 📊 Dataset Information

### English Dataset

- **Source**: Google Drive (ID: `1N7rk-kfnDFIGMeX0ROVTjKh71gcgx-7R`)
- **Format**: CSV with Message and Category columns
- **Size**: ~5,500 samples
- **Labels**: ham, spam

### Vietnamese Dataset

- **Source**: Kaggle (`victorhoward2/vietnamese-spam-post-in-social-network`)
- **Format**: CSV with texts_vi and label columns
- **Size**: ~3,000 samples
- **Labels**: ham, spam

### Data Augmentation Techniques

1. **Hard Negative Mining** (α=0.3)
   - Mixes legitimate messages with spam-like phrases
   - Creates challenging boundary cases

2. **Synonym Replacement** (20% augmentation)
   - Uses NLTK WordNet for English
   - Maintains semantic meaning

3. **Class Balancing**
   - Oversamples minority class
   - Applies class weights during training

---

## ⚙️ Configuration

### Backend Configuration

Edit `backend/.env` or use environment variables:

```bash
# Model Settings
MODEL_NAME=intfloat/multilingual-e5-base
DEFAULT_K=5
DEFAULT_ALPHA=0.8
MAX_SEQUENCE_LENGTH=512

# API Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
MAX_MESSAGE_LENGTH=10000
RATE_LIMIT=100

# Paths
FAISS_INDEX_PATH=artifacts/faiss_index.bin
METADATA_PATH=artifacts/train_metadata.json
```

### Frontend Configuration

Edit `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_TELEMETRY_DISABLED=1
```

---

## 💻 Development

### Project Structure

```
spam-filter-ai/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes & schemas
│   │   ├── core/        # Configuration
│   │   ├── services/    # Model service
│   │   ├── middleware/  # Logging, rate limiting
│   │   └── utils/       # Utilities
│   ├── tests/           # Unit & integration tests
│   └── main.py          # Application entry point
├── frontend/            # Next.js frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Next.js pages
│   │   └── styles/      # CSS styles
│   └── public/          # Static assets
├── scripts/             # Training & deployment scripts
│   ├── data_loader.py   # Dataset loading
│   ├── augmentation.py  # Data augmentation
│   ├── train_model.py   # Model training
│   └── run_pipeline.py  # Complete pipeline
├── artifacts/           # Model artifacts (generated)
└── data/                # Dataset storage (generated)
```

### Code Style

```bash
# Backend
cd backend
black app/
flake8 app/
mypy app/

# Frontend
cd frontend
npm run lint
npm run format
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

### API Integration Tests

```bash
bash scripts/quick_test.sh
```

### Frontend Tests

```bash
cd frontend
npm test
npm run test:e2e
```

---

## 🔧 Troubleshooting

### Common Issues

**1. Missing artifacts error**

```
Error: artifacts directory not found
```

**Solution:** Train the model first:
```bash
cd backend && source venv/bin/activate
cd ../scripts && python run_pipeline.py
```

**2. Docker build fails**

```
Error: Cannot connect to Docker daemon
```

**Solution:** Ensure Docker Desktop is running

**3. Port already in use**

```
Error: Port 8000 already in use
```

**Solution:** Stop existing services:
```bash
docker-compose down
# or
lsof -ti:8000 | xargs kill
```

**4. Frontend cannot connect to backend**

**Solution:** Check CORS settings in `backend/.env`:
```bash
CORS_ORIGINS=http://localhost:3000
```

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint/Prettier for TypeScript/JavaScript
- Write tests for new features
- Update documentation as needed

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **HuggingFace** for the multilingual-e5-base model
- **FAISS** for efficient similarity search
- **FastAPI** and **Next.js** communities
- Dataset contributors on Google Drive and Kaggle

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/spam-filter-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/spam-filter-ai/discussions)
- **Email**: your.email@example.com

---

## 🗺️ Roadmap

- [ ] Multi-language support (Spanish, French, German)
- [ ] Real-time monitoring dashboard
- [ ] A/B testing framework
- [ ] Advanced spam subcategories
- [ ] Mobile app support
- [ ] Cloud deployment guides (AWS, GCP, Azure)

---

**Built with ❤️ for spam detection and AI explainability**
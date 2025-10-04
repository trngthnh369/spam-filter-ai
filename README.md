# 🛡️ Spam Filter AI - Production-Ready System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14.1-black.svg)](https://nextjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An enterprise-grade AI-powered spam detection system with explainability, supporting English & Vietnamese messages. Built with multilingual E5 embeddings, FAISS vector search, and weighted KNN classification.

![Spam Filter AI Demo](docs/demo.png)

## 🌟 Key Features

### Core Capabilities
- **✅ Multilingual Support**: Handles both English and Vietnamese text seamlessly
- **✅ High Accuracy**: 95-98% accuracy with optimized weighted KNN classifier
- **✅ Explainable AI**: Token-level saliency analysis showing which words influence predictions
- **✅ Spam Subcategorization**: Automatically categorizes spam into Advertising, System/Security, or Other
- **✅ Real-time Classification**: Fast inference with FAISS-accelerated vector search
- **✅ Production-Ready API**: RESTful FastAPI backend with comprehensive documentation

### Technical Highlights
- **State-of-the-art Embeddings**: Uses `intfloat/multilingual-e5-base` (768-dim)
- **Efficient Search**: FAISS IndexFlatIP for cosine similarity search
- **Smart Augmentation**: Hard example generation + synonym replacement
- **Class Imbalance Handling**: Weighted voting with optimized alpha parameter
- **Comprehensive Testing**: Unit tests, integration tests, and API tests included

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │ Classifier   │  │   Result     │  │  Stats Panel    │   │
│  │    Form      │  │   Display    │  │                 │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ▼
                    HTTP/REST API (FastAPI)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend Services                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Model Service (ModelLoader)                         │   │
│  │  • Multilingual-E5 embeddings (768-dim)             │   │
│  │  • FAISS IndexFlatIP (cosine similarity)            │   │
│  │  • Weighted KNN with optimized alpha                │   │
│  │  • Masking-based token saliency                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Training Pipeline                         │
│  Data Loading → Augmentation → Training → Artifacts         │
│  • Google Drive (English dataset)                           │
│  • Kaggle (Vietnamese dataset)                              │
│  • Hard example generation                                  │
│  • Synonym replacement (NLTK WordNet)                       │
│  • Alpha optimization                                       │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (for deployment)
- 8GB+ RAM recommended

### Installation

1. **Clone Repository**
```bash
git clone https://github.com/trngthnh369/spam-filter-ai.git
cd spam-filter-ai
```

2. **Setup Environment**
```bash
# Run automated setup
bash scripts/setup.sh

# Or manually:
make install
make setup
```

3. **Train Model**
```bash
# Run complete pipeline (downloads data, augments, trains)
make train

# Or run Python script directly:
cd scripts
python run_pipeline.py
```

Expected output:
```
[STEP 1] Loading datasets...
Loaded 5572 English samples
Loaded 3000+ Vietnamese samples

[STEP 2] Augmenting data...
Generated 500+ hard ham examples
Generated 1200+ synonym replacements

[STEP 3] Training model...
Optimizing alpha parameter...
Best alpha: 0.8 with accuracy: 0.9650

✓ Artifacts saved to artifacts/
```

4. **Deploy with Docker**
```bash
make deploy

# Services will be available at:
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Frontend: http://localhost:3000
```

### Manual Deployment (Development)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 📊 Dataset Information

### English Dataset
- **Source**: Google Drive (`1N7rk-kfnDFIGMeX0ROVTjKh71gcgx-7R`)
- **Format**: CSV with Message and Category columns
- **Labels**: ham, spam
- **Size**: ~5,500 samples

### Vietnamese Dataset
- **Source**: Kaggle (`victorhoward2/vietnamese-spam-post-in-social-network`)
- **Format**: CSV with texts_vi and label columns
- **Labels**: ham, spam
- **Size**: ~3,000 samples

### Data Augmentation
- **Hard Ham Generation**: Creates ham messages with spam-like phrases (α=0.3)
- **Synonym Replacement**: NLTK WordNet-based (20% augmentation ratio)
- **Total Increase**: 20-30% more training samples

## 🎯 API Usage

### Single Classification
```bash
curl -X POST "http://localhost:8000/api/v1/classify" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Win free iPhone now!",
    "k": 5,
    "explain": true
  }'
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

### Batch Classification
```bash
curl -X POST "http://localhost:8000/api/v1/classify/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      "Hello friend",
      "Click here for prize",
      "Meeting at 3pm"
    ],
    "k": 5
  }'
```

### Explainability Endpoint
```bash
curl -X POST "http://localhost:8000/api/v1/explain" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Congratulations! You won $1000",
    "k": 10
  }'
```

### Statistics
```bash
curl "http://localhost:8000/api/v1/stats"
```

## 🔬 Model Details

### Embeddings
- **Model**: `intfloat/multilingual-e5-base`
- **Dimension**: 768
- **Max Length**: 512 tokens
- **Pooling**: Average pooling with attention mask

### Classification Algorithm
```
Weight = (1 - α) × similarity × class_weight + α × saliency_weight

Where:
- α (alpha): Balance between similarity and saliency (optimized: 0.8)
- similarity: Cosine similarity from FAISS search
- class_weight: Handles class imbalance
- saliency_weight: Quick keyword-based spam signal
```

### Explainability
- **Method**: Masking-based token saliency
- **Process**: Removes each token, measures prediction change
- **Output**: Per-token importance scores (0-1)

## 📈 Performance Metrics

| Metric | Value |
|--------|-------|
| Overall Accuracy | 95-98% |
| Precision (Spam) | 93-96% |
| Recall (Spam) | 90-95% |
| F1-Score | 92-96% |
| Inference Time | <50ms |

## 🛠️ Development

### Project Structure
```
spam-filter-ai/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes & schemas
│   │   ├── core/        # Configuration
│   │   ├── services/    # Model service
│   │   └── middleware/  # Logging, rate limiting
│   ├── tests/           # Unit & integration tests
│   └── main.py          # Entry point
├── frontend/            # Next.js frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   └── pages/       # Next.js pages
│   └── public/          # Static assets
├── scripts/             # Training & deployment
│   ├── data_loader.py   # Dataset loading
│   ├── augmentation.py  # Data augmentation
│   ├── train_model.py   # Model training
│   └── run_pipeline.py  # Complete pipeline
├── artifacts/           # Model artifacts (generated)
│   ├── faiss_index.bin
│   ├── train_metadata.json
│   ├── class_weights.json
│   └── model_config.json
└── docker-compose.yml   # Docker deployment
```

### Running Tests
```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test

# API integration tests
bash scripts/quick_test.sh
```

### Configuration
Edit `backend/app/core/config.py` or use environment variables:

```bash
# Model settings
MODEL_NAME=intfloat/multilingual-e5-base
DEFAULT_K=5
DEFAULT_ALPHA=0.8

# Augmentation
AUG_RATIO=0.2
ALPHA_HAM=0.3

# API
MAX_MESSAGE_LENGTH=10000
RATE_LIMIT=100
```

## 🔄 Retraining

To retrain with new data:

```bash
# 1. Add your data to data/new_data.csv
# 2. Run pipeline
python scripts/run_pipeline.py --aug-ratio 0.3

# 3. Restart services
docker-compose restart backend
```

## 📚 Documentation

- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Redoc**: http://localhost:8000/redoc
- **Architecture**: See [ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Training Guide**: See [TRAINING.md](docs/TRAINING.md)

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- **HuggingFace** for multilingual-e5-base model
- **FAISS** for efficient similarity search
- **FastAPI** and **Next.js** communities
- Dataset contributors on Google Drive and Kaggle

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/spam-filter-ai/issues)
- **Email**: your.email@example.com
- **Documentation**: [Wiki](https://github.com/yourusername/spam-filter-ai/wiki)

---

**Built with ❤️ for spam detection and AI explainability**
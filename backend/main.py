"""
FastAPI Backend for Spam Filter AI
Main entry point for the API server
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core import settings
from app.api import classifier, health, explain
from app.services import ModelService


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global model service instance
model_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for loading and unloading models."""
    global model_service
    
    logger.info("Starting application ...")
    logger.info("Loading model and FAISS index ...")

    try:
        model_service = ModelService()
        model_service.load_model()
        app.state.model_service = model_service
        logger.info("Model and FAISS index loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load model or FAISS index: {e}")
        raise 
    yield
    
    logger.info("Shutting down application ...")
    # Clean up resources if needed


# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered spam detection service with explainability",
    lifespan=lifespan
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routers
app.include_router(health.router, prefix=settings.API_V1_STR, tags=["health"])
app.include_router(classifier.router, prefix=settings.API_V1_STR, tags=["classifier"])
app.include_router(explain.router, prefix=settings.API_V1_STR, tags=["explain"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to the Spam Filter AI API. Visit /docs for API documentation.",
        "version": settings.VERSION,
        "docs_url": "/docs"
    }
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
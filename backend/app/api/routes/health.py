"""Health check endpoints"""

from fastapi import APIRouter, Request, Depends
from app.api import HealthResponse
from app.core import settings
from app.services import ModelService


router = APIRouter()

def get_model_service(request: Request) -> ModelService:
    """Dependency to get model service instance."""
    return request.app.state.model_service

@router.get("/health", response_model=HealthResponse)
async def health_check(model_service: ModelService = Depends(get_model_service)):
    """Health check endpoint."""
    model_loaded = (
        model_service.model is not None and
        model_service.index is not None and
        model_service.train_metadata is not None
    )

    faiss_size = model_service.index.ntotal if model_service.index else None
    return HealthResponse(
        status="healthy" if model_loaded else "unhealthy",
        version=settings.VERSION,
        model_loaded=model_loaded,
        faiss_index_size=faiss_size
    )
"""
Classification API endpoints
"""

from fastapi import APIRouter, HTTPException, Request, Depends
import time
import logging

from app.api import (
    ClassifyRequest, ClassifyResponse, 
    BatchClassifyRequest, BatchClassifyResponse,
    VoteScores, NeighborInfo, TokenSaliency
)
from app.services import ModelService

logger = logging.getLogger(__name__)
router = APIRouter()


def get_model_service(request: Request) -> ModelService:
    """Dependency to get model service instance."""
    return request.app.state.model_service

@router.post("/classify", response_model=ClassifyResponse)
async def classify_message(
    req: ClassifyRequest,
    model_service: ModelService = Depends(get_model_service)
):
    """
    Classify a single message as spam or ham
    
    - **message**: Text message to classify
    - **k**: Number of neighbors for KNN (default: 5)
    - **alpha**: Saliency weight parameter (default: from config)
    - **explain**: Include detailed token-level explainability
    """
    start_time = time.time()
    
    try:
        
        #Perform classification
        result = model_service.classify_weighted_knn(
            text=req.message,
            k=req.k,
            alpha=req.alpha,
        )
        
        # Get subcategory if spam
        subcategory = None
        if result['prediction'] == 'spam':
            subcategory = model_service.classify_spam_subcategory(req.message)
            
        # Get token saliency if requested
        tokens = None
        if req.explain:
            token_saliencies = model_service.compute_token_saliency(
                text=req.message,
                k=req.k
            )
            tokens = [TokenSaliency(**ts) for ts in token_saliencies]
            
        # Build response
        processing_time = (time.time() - start_time) * 1000  # in ms
        response = ClassifyResponse(
            prediction=result['prediction'],
            is_spam=(result['prediction'] == 'spam'),
            confidence=result['confidence'],
            vote_scores=VoteScores(**result['vote_scores']),
            subcategory=subcategory,
            saliency_weight=result['saliency_weight'],
            alpha=result['alpha'],
            neighbors=[NeighborInfo(**n) for n in result['neighbors']],
            tokens=tokens,
            processing_time_ms=processing_time
        )
        logger.info(f"Classified message: {result['prediction']} (confidence: {result['confidence']:.3f})")
        return response
            
        
    except Exception as e:
        logger.error(f"Error during classification: {e}")
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")
    
@router.post("/classify/batch", response_model=BatchClassifyResponse)
async def classify_batch(
    req: BatchClassifyRequest,
    model_service: ModelService = Depends(get_model_service)
):
    """
    Classify a batch of messages as spam or ham
    
    - **messages**: List of text messages to classify
    - **k**: Number of neighbors for KNN (default: 5)
    - **alpha**: Saliency weight parameter (default: from config)
    - **explain**: Include detailed token-level explainability
    """
    start_time = time.time()
    
    try:
        results = []
        
        for message in req.messages:
            # Create individual request
            single_req = ClassifyRequest(
                message=message,
                k=req.k,
                alpha=req.alpha,
                explain=req.explain
            )
            
            # Classify message
            result = await classify_message(single_req, model_service)
            results.append(result)
            
        processing_time = (time.time() - start_time) * 1000  # in ms
        
        response = BatchClassifyResponse(
            results=results,
            total_processed=len(results),
            processing_time_ms=processing_time
        )
        
        logger.info(f"Batch classified {len(results)} messages in {processing_time:.2f} ms")
        return response
        
    except Exception as e:
        logger.error(f"Error during batch classification: {e}")
        raise HTTPException(status_code=500, detail=f"Batch classification failed: {str(e)}")
    
@router.get("/stats")
async def get_statistics(
    model_service: ModelService = Depends(get_model_service)
):
    """Get model statistics and metadata."""
    try:
        
        total_samples = len(model_service.train_metadata)
        
        # Count label distribution
        label_counts = {}
        for item in model_service.train_metadata:
            label = item['label']
            label_counts[label] = label_counts.get(label, 0) + 1
            
        return {
            "total_training_samples": total_samples,
            "label_distribution": label_counts,
            "class_weights": model_service.class_weights,
            "model_name": model_service.config.get("model_name"),
            "best_alpha": model_service.config.get("best_alpha"),
            "faiss_index_size": model_service.index.ntotal
        }
        
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch statistics: {str(e)}")
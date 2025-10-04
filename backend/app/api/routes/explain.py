"""
Explainability endpoints.
"""

from fastapi import APIRouter, Request, Depends, HTTPException
import logging
from app.api import (
    ExplainResponse, ExplainRequest,
    NeighborInfo, TokenSaliency
)
from app.services import ModelService

logger = logging.getLogger(__name__)
router = APIRouter()

def get_model_service(request: Request) -> ModelService:
    """Dependency to get model service instance."""
    return request.app.state.model_service

@router.post("/explain", response_model=ExplainResponse)
async def explain_prediction(
    req: ExplainRequest,
    model_service: ModelService = Depends(get_model_service)
):
    """Get detailed explainability for message prediction."""
    try:
        result = model_service.classify_weighted_knn(
            text=req.message,
            k=req.k
        )
        token_saliencies = model_service.compute_token_saliency(
            text=req.message,
            k=req.k
        )
        tokens = [TokenSaliency(**ts) for ts in token_saliencies]

        spam_indicators = []
        ham_indicators = []
        
        for neighbor in result['neighbors']:
            if neighbor['label'] == 'spam' and neighbor['similarity'] > 0.7:
                spam_indicators.append(f"Similar to: {neighbor['message'][:50]}...")
            elif neighbor['label'] == 'ham' and neighbor['similarity'] > 0.7:
                ham_indicators.append(f"Similar to: {neighbor['message'][:50]}...")

        high_saliency_tokens = [t for t in token_saliencies if t['saliency'] > 0.5]
        if high_saliency_tokens:
            spam_indicators.append(f"High-impact words: {', '.join([t['token'] for t in high_saliency_tokens[:5]])}")

        analysis = f"This message was classified as {result['prediction'].upper()} with {result['confidence']*100:.2f}% confidence."
        
        if result['prediction'] == 'spam':
            analysis += f"Spam indicators detected with saliency weight of {result['saliency_weight']:.3f}. "
            analysis += f"The message shares similarities with {len([n for n in result['neighbors'] if n['label']=='spam'])} spam examples in the training data."
        else:
            analysis += f"The message appears legitimate based on {len([n for n in result['neighbors'] if n['label']=='ham'])} similar ham examples."
        
        return ExplainResponse(
            message=req.message,
            prediction=result['prediction'],
            tokens=tokens,
            top_neighbors=[NeighborInfo(**n) for n in result['neighbors'][:5]],
            spam_indicators=spam_indicators[:10],
            ham_indicators=ham_indicators[:10],
            analysis=analysis
        )
    
    except Exception as e:
        logger.error(f"Error in explain endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")
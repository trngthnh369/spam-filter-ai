"""
Pydantic schemas for response/ request validation.
"""


from pydantic import BaseModel, Field, validator
from typing import List, Optional
from enum import Enum


class LabelEnum(str, Enum):
    """Classification labels."""
    HAM = "ham"
    SPAM = "spam"

    
class SpamSubcategoryEnum(str, Enum):
    """Spam subcategories."""
    QUANGCAO = "spam_quangcao"
    HETHONG = "spam_hethong"
    KHAC = "spam_khac"


class ClassifyRequest(BaseModel):
    """Request model for classification."""
    message: str = Field(..., min_length=1, max_length=10000, description="Message text to classify")
    k: Optional[int] = Field(5, ge=1, le=20, description="Number of neighbors for KNN")
    alpha: Optional[float] = Field(0.8, ge=0.0, le=1.0, description="Saliency weight parameter")
    explain: bool = Field(False, description="Include detailed explainability")

    @validator('message')
    def validate_massage(cls, v):
        if not v.strip():
            raise ValueError('Message must not be empty or whitespace')
        return v.strip()
    
    
class NeighborInfo(BaseModel):
    """Information about a neighbor in KNN."""
    label: LabelEnum
    similarity: float = Field(..., ge=0.0, le=1.0)
    weight: float
    message: str = Field(..., max_length=200)

    
class VoteScores(BaseModel):
    """Vote scores for each class."""
    ham: float
    spam: float


class TokenSaliency(BaseModel):
    """Token level saliency information."""
    token: str
    saliency: float = Field(..., ge=0.0, le=1.0)

    
class ClassifyResponse(BaseModel):
    """Response model for classification."""
    prediction: LabelEnum
    is_spam: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    vote_scores: VoteScores
    subcategory: Optional[SpamSubcategoryEnum] = None
    saliency_weight: float
    alpha: float
    neighbors: List[NeighborInfo]
    tokens: Optional[List[TokenSaliency]] = None
    processing_time_ms: float
    
    
class BatchClassifyRequest(BaseModel):
    """Request model fro batch classification."""
    messages: List[str] = Field(..., min_items=1, max_items=100)
    k: Optional[int] = Field(5, ge=1, le=20)
    alpha: Optional[float] = Field(None, ge=0.0, le=1.0)
    explain: bool = Field(False)
    
    
class BatchClassifyResponse(BaseModel):
    """Response model for batch classification."""
    results: List[ClassifyResponse]
    total_processed: int
    processing_time_ms: float
    
    
class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    model_loaded: bool
    faiss_index_size: Optional[int] = None
    
    
class ExplainRequest(BaseModel):
    """Request for detailed explainability."""
    message: str = Field(..., min_length=1, max_length=10000)
    k: Optional[int] = Field(10, ge=1, le=50)


class ExplainResponse(BaseModel):
    """Detailed explainability response."""
    message: str
    prediction: LabelEnum
    tokens: List[TokenSaliency]
    top_neighbors: List[NeighborInfo]
    spam_indicators: List[str]
    ham_indicators: List[str]
    analysis: str
    
    
class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None
    timestamp: str
"""
Model service unit tests
"""

import pytest
import numpy as np
from app.services.model_loader import ModelService


class TestModelService:
    """Test ModelService class"""
    
    @pytest.fixture
    def model_service(self):
        """Create model service instance"""
        service = ModelService()
        # Note: In real tests, you'd mock the model loading
        return service
    
    def test_compute_quick_saliency(self, model_service):
        """Test quick saliency computation"""
        # High spam signal
        spam_text = "Win $1000 free money now!"
        saliency = model_service.compute_quick_saliency(spam_text)
        assert saliency > 0.3
        
        # Low spam signal
        ham_text = "Hello, how are you?"
        saliency = model_service.compute_quick_saliency(ham_text)
        assert saliency < 0.5
    
    def test_classify_spam_subcategory(self, model_service):
        """Test spam subcategory classification"""
        # Advertising spam
        ad_text = "Sale 80% off! Buy now!"
        subcategory = model_service.classify_spam_subcategory(ad_text)
        assert subcategory == "spam_quangcao"
        
        # Security spam
        security_text = "Your account will be suspended. Verify now!"
        subcategory = model_service.classify_spam_subcategory(security_text)
        assert subcategory == "spam_hethong"
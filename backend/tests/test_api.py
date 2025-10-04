"""
API endpoint tests
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self):
        """Test health endpoint returns 200"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data


class TestClassificationEndpoint:
    """Test classification endpoints"""
    
    def test_classify_ham_message(self):
        """Test classifying a legitimate message"""
        payload = {
            "message": "Hello, how are you doing today?",
            "k": 5,
            "explain": False
        }
        response = client.post("/api/v1/classify", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert data["prediction"] in ["ham", "spam"]
        assert "confidence" in data
        assert 0 <= data["confidence"] <= 1
    
    def test_classify_spam_message(self):
        """Test classifying a spam message"""
        payload = {
            "message": "Congratulations! You've won $1000! Click here now!",
            "k": 5,
            "explain": False
        }
        response = client.post("/api/v1/classify", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["prediction"] == "spam"
        assert data["is_spam"] is True
        assert "subcategory" in data
    
    def test_classify_with_explainability(self):
        """Test classification with explainability enabled"""
        payload = {
            "message": "Win free iPhone now!",
            "k": 5,
            "explain": True
        }
        response = client.post("/api/v1/classify", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "tokens" in data
        assert data["tokens"] is not None
        assert len(data["tokens"]) > 0
    
    def test_classify_empty_message(self):
        """Test classifying empty message returns error"""
        payload = {
            "message": "",
            "k": 5
        }
        response = client.post("/api/v1/classify", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_classify_vietnamese_message(self):
        """Test Vietnamese message classification"""
        payload = {
            "message": "Chào bạn, hẹn gặp lại nhé!",
            "k": 5
        }
        response = client.post("/api/v1/classify", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data


class TestBatchClassification:
    """Test batch classification endpoint"""
    
    def test_batch_classify(self):
        """Test batch classification of multiple messages"""
        payload = {
            "messages": [
                "Hello friend",
                "Win $1000 now!",
                "Meeting at 3pm"
            ],
            "k": 5
        }
        response = client.post("/api/v1/classify/batch", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 3
        assert data["total_processed"] == 3
    
    def test_batch_classify_empty_list(self):
        """Test batch classification with empty list"""
        payload = {"messages": []}
        response = client.post("/api/v1/classify/batch", json=payload)
        assert response.status_code == 422


class TestExplainEndpoint:
    """Test explainability endpoint"""
    
    def test_explain_prediction(self):
        """Test getting detailed explanation"""
        payload = {
            "message": "Congratulations! You won $1000",
            "k": 10
        }
        response = client.post("/api/v1/explain", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "tokens" in data
        assert "spam_indicators" in data
        assert "ham_indicators" in data
        assert "analysis" in data


class TestStatsEndpoint:
    """Test statistics endpoint"""
    
    def test_get_stats(self):
        """Test getting model statistics"""
        response = client.get("/api/v1/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_training_samples" in data
        assert "label_distribution" in data
        assert "class_weights" in data
        assert "best_alpha" in data
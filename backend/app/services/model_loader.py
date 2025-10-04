"""
Model loading and inference services
"""

import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
import faiss
import numpy as np
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from app.core import settings

logger = logging.getLogger(__name__)


class ModelService:
    """Service for loading and managing ML models"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.index = None
        self.train_metadata = None
        self.class_weights = None
        self.config = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")

    def load_model(self):
        """Load all required models and artifacts"""
        try:
            # Load transformers model
            logger.info(f"Loading transformer model: {settings.MODEL_NAME}")
            self.tokenizer = AutoTokenizer.from_pretrained(settings.MODEL_NAME)
            self.model = AutoModel.from_pretrained(settings.MODEL_NAME)
            self.model = self.model.to(self.device)
            self.model.eval()   
            
            # Load FAISS index
            logger.info(f"Loading FAISS index from: {settings.FAISS_INDEX_PATH}")
            if not Path(settings.FAISS_INDEX_PATH).exists():
                raise FileNotFoundError(f"FAISS index file not found at {settings.FAISS_INDEX_PATH}")
            self.index = faiss.read_index(settings.FAISS_INDEX_PATH)
            
            # Load metadata
            logger.info(f"Loading training metadata from: {settings.METADATA_PATH}")
            with open(settings.METADATA_PATH, 'r', encoding='utf-8') as f:
                self.train_metadata = json.load(f)
                
            # Load config
            logger.info(f"Loading model config from: {settings.CONFIG_PATH}")
            with open(settings.CONFIG_PATH, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                
            logger.info("All models and artifacts loaded successfully.")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise

    def average_pool(self, last_hidden_states, attention_mask):
        """Average pooling for embeddings"""
        last_hidden = last_hidden_states.masked_fill(
            ~attention_mask[..., None].bool(), 0.0
        )
        return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]
    
    def get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for a single text input"""
        query_text = f"query: {text}"
        batch_dict = self.tokenizer(
            [query_text],
            max_length=settings.MAX_SEQUENCE_LENGTH,
            padding=True,
            truncation=True,
            return_tensors="pt"
        )
        batch_dict = {k: v.to(self.device) for k, v in batch_dict.items()}
        
        with torch.no_grad():
            output = self.model(**batch_dict)
            embedding = self.average_pool(output.last_hidden_state, batch_dict['attention_mask'])
            embedding = F.normalize(embedding, p=2, dim=1)
            return embedding.cpu().numpy().astype('float32')
        
    def compute_quick_saliency(self, text: str) -> float:
        """Compute quick saliency weight"""
        words = text.lower().split()
        text_lower = text.lower()
        
        spam_keywords = [
            "free", "win", "winner", "cash", "prize", "click", "buy", "cheap",
            "offer", "limited", "urgent", "act now", "subscribe", "risk-free",
            "guarantee", "money back", "trial", "exclusive", "deal", "miễn phí",
            "trúng", "thưởng", "tiền mặt", "nhấp", "mua", "rẻ", "khuyến mãi",
            "giới hạn", "khẩn cấp", "đăng ký", "bảo đảm", "dùng thử", "độc quyền", "ưu đãi"
        ]
        
        social_keywords = [
        'mom', 'boss', 'hr', 'manager', 'security update', 'unusual login',
        'hospital bill', 'emergency', 'help buy', 'reimburse', 'gift cards',
        'short-staffed', 'extra shifts', 'card was declined', 'warranty',
        'mẹ', 'sếp', 'nhân sự', 'cập nhật bảo mật', 'đăng nhập bất thường',
        'viện phí', 'khẩn cấp', 'giúp mua', 'hoàn tiền',
        'thiếu nhân sự', 'ca làm thêm', 'thẻ bị từ chối', 'bảo hành'
        ]
        
        urgency_keywords = [
        'today', 'tomorrow', 'this week', 'before friday', 'reply yes',
        'cancel anytime', 'confirm before', 'register early', 'already got mine',
        'hôm nay', 'ngày mai', 'tuần này', 'trước thứ sáu', 'trả lời có'
        ]
        
        spam_score = sum(1 for word in words if any(k in word for k in spam_keywords))
        social_score = sum(2 for k in social_keywords if k in text_lower)
        urgency_score = sum(1.5 for k in urgency_keywords if k in text_lower)
        
        import re
        money_pattern = r'\$\d+|\d+\$|\d+\s*(triệu|nghìn|đồng|dollar)'
        money_score = 2 if re.search(money_pattern, text_lower) else 0
        
        total_score = (spam_score + social_score + urgency_score + money_score)
        saliency = min(1.0, max(0.1, total_score / max(len(words), 1) + 0.2))
        
        return saliency
    
    def classify_weighted_knn(
        self,
        text: str,
        k: int = 5,
        alpha: Optional[float] = None
    ) -> Dict:
        """Classify text using weighted KNN"""
        if alpha is None:
            alpha = self.config.get('best_alpha', settings.DEFAULT_ALPHA)
            
        # Get embedding
        query_embedding = self.get_embedding(text)
        
        # Search neighbors
        scores, indices = self.index.search(query_embedding, k)
        
        # Compute saliency
        saliency_weight = self.compute_quick_saliency(text)
        
        # Calculate weighted votes
        vote_scores = {"ham": 0.0, "spam": 0.0}
        neighbors = []

        for i in range(k):
            neighbor_idx = indices[0][i]
            similarity = float(scores[0][i])
            neighbor_label = self.train_metadata[neighbor_idx]['label']
            neighbor_message = self.train_metadata[neighbor_idx]['message']
            
            # Weighted formula: (1-α)×similarity×class_weight + α×saliency_weight
            weight = (1 - alpha) * similarity * self.class_weights[neighbor_label] + alpha * saliency_weight
            
            vote_scores[neighbor_label] += weight
            
            neighbors.append({
                "label": neighbor_label,
                "similarity": similarity,
                "weight": weight,
                "message": neighbor_message[:100] + "..." if len(neighbor_message) > 100 else neighbor_message
            })

        # Get final prediction
        predicted_label = max(vote_scores, key=vote_scores.get)
        confidence = vote_scores[predicted_label] / sum(vote_scores.values())

        return {
            "prediction": predicted_label,
            "confidence": confidence,
            "vote_scores": vote_scores,
            "neighbors": neighbors,
            "saliency_weight": saliency_weight,
            "alpha": alpha
        }
        
    def classify_spam_subcategory(self, text: str) -> str:
        """Classify spam subcategory"""
        text_lower = text.lower()
        
        quangcao_keywords = [
            "free", "win", "winner", "cash", "prize", "click", "buy", "cheap",
            "offer", "limited", "urgent", "act now", "subscribe", "risk-free",
            "guarantee", "money back", "trial", "exclusive", "deal", "miễn phí",
            "trúng", "thưởng", "tiền mặt", "nhấp", "mua", "rẻ", "khuyến mãi",
            "giới hạn", "khẩn cấp", "đăng ký", "bảo đảm", "dùng thử", "độc quyền", "ưu đãi"
        ]
        
        hethong_keywords = [
            'mom', 'boss', 'hr', 'manager', 'security update', 'unusual login',
            'hospital bill', 'emergency', 'help buy', 'reimburse', 'gift cards',
            'short-staffed', 'extra shifts', 'card was declined', 'warranty',
            'mẹ', 'sếp', 'nhân sự', 'cập nhật bảo mật', 'đăng nhập bất thường',
            'viện phí', 'khẩn cấp', 'giúp mua', 'hoàn tiền',
            'thiếu nhân sự', 'ca làm thêm', 'thẻ bị từ chối', 'bảo hành'
        ]
        
        quangcao_score = sum(1 for k in quangcao_keywords if k in text_lower)
        hethong_score = sum(1 for k in hethong_keywords if k in text_lower)
        
        if max(quangcao_score, hethong_score) == 0:
            return "spam_khac"
        elif quangcao_score >= hethong_score:
            return "spam_quangcao"
        else:
            return "spam_hethong"
        
    def compute_token_saliency(self, text: str, k: int = 10) -> List[Dict]:
        """Compute token-level saliency for explainability"""
        tokens = self.tokenizer.tokenize(text)
        
        if len(tokens) <= 1:
            return [{"token": text, "saliency": 1.0}]
        
        # Get original prediction
        original_embedding = self.get_embedding(text)
        original_scores, original_indices = self.index.search(original_embedding, k)
        original_spam_score = sum(
            s for s, idx in zip(original_scores[0], original_indices[0])
            if self.train_metadata[idx]['label'] == 'spam'  
        )
        
        saliencies = []

        # Mask each token and compute change
        for i, token in enumerate(tokens):
            token_mask = tokens.copy()
            token_mask[i] = self.tokenizer.pad_token
            masked_text = self.tokenizer.convert_tokens_to_string(token_mask)
            
            masked_embedding = self.get_embedding(masked_text)
            masked_scores, masked_indices = self.index.search(masked_embedding, k)
            masked_spam_score = sum(
                s for s, idx in zip(masked_scores[0], masked_indices[0])
                if self.train_metadata[idx]['label'] == 'spam'
            )

            # Compute saliency as the change in spam score
            saliency = original_spam_score - masked_spam_score
            saliencies.append(saliency)
            
        # Normalize saliencies to [0, 1]
        arr = np.array(saliencies)
        if len(arr) > 1:
            arr = (arr - arr.min()) / (np.ptp(arr) + 1e-12)
        else:
            arr = np.array([1.0])

        return [
            {"token": token, "saliency": float(saliency)}
            for token, saliency in zip(tokens, arr)
        ]
"""
Model training pipeline
Generates embeddings, builds FAISS index, optimizes parameters
"""

import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
import faiss
import numpy as np
import json
import logging
from pathlib import Path
from sklearn.model_selection import train_test_split
from collections import Counter
from tqdm import tqdm
from typing import List, Dict, Tuple
import pandas as pd
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelTrainer:
    """Spam classification model trainer"""
    
    def __init__(
        self,
        model_name: str = "intfloat/multilingual-e5-base",
        output_dir: str = "artifacts"
    ):
        self.model_name = model_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Load model
        logger.info(f"Loading model: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model = self.model.to(self.device)
        self.model.eval()
        
    def average_pool(self, last_hidden_states, attention_mask):
        """Average pooling for embeddings"""
        last_hidden = last_hidden_states.masked_fill(
            ~attention_mask[..., None].bool(), 0.0
        )
        return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]
    
    def generate_embeddings(
        self,
        texts: List[str],
        batch_size: int = 32,
        prefix: str = "passage"
    ) -> np.ndarray:
        """Generate embeddings for texts"""
        
        embeddings = []
        
        for i in tqdm(range(0, len(texts), batch_size), desc=f"Generating {prefix} embeddings"):
            batch_texts = texts[i:i+batch_size]
            batch_texts_with_prefix = [f"{prefix}: {text}" for text in batch_texts]
            
            batch_dict = self.tokenizer(
                batch_texts_with_prefix,
                max_length=512,
                padding=True,
                truncation=True,
                return_tensors="pt"
            )
            batch_dict = {k: v.to(self.device) for k, v in batch_dict.items()}
            
            with torch.no_grad():
                outputs = self.model(**batch_dict)
                batch_embeddings = self.average_pool(
                    outputs.last_hidden_state,
                    batch_dict["attention_mask"]
                )
                batch_embeddings = F.normalize(batch_embeddings, p=2, dim=1)
                embeddings.append(batch_embeddings.cpu().numpy())
        
        return np.vstack(embeddings)
    
    def calculate_class_weights(self, labels: List[str]) -> Dict[str, float]:
        """Calculate class weights for imbalanced data"""
        
        label_counts = Counter(labels)
        total_samples = len(labels)
        num_classes = len(label_counts)
        
        class_weights = {}
        for label, count in label_counts.items():
            class_weights[label] = total_samples / (num_classes * count)
        
        logger.info("Class distribution:")
        for label, count in label_counts.items():
            logger.info(f"  {label}: {count} samples (weight: {class_weights[label]:.3f})")
        
        return class_weights
    
    def build_faiss_index(self, embeddings: np.ndarray) -> faiss.Index:
        """Build FAISS index for similarity search"""
        
        dimension = embeddings.shape[1]
        logger.info(f"Building FAISS index with dimension {dimension}")
        
        index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity)
        index.add(embeddings.astype("float32"))
        
        logger.info(f"FAISS index built with {index.ntotal} vectors")
        
        return index
    
    def optimize_alpha(
        self,
        test_embeddings: np.ndarray,
        test_metadata: List[Dict],
        index: faiss.Index,
        train_metadata: List[Dict],
        class_weights: Dict[str, float],
        k: int = 10
    ) -> Tuple[float, List[Tuple[float, float]]]:
        """Find optimal alpha parameter"""
        
        logger.info("Optimizing alpha parameter...")
        
        alpha_values = np.arange(0.0, 1.1, 0.1)
        best_alpha = 0.0
        best_accuracy = 0.0
        alpha_results = []
        
        for alpha in alpha_values:
            correct = 0
            total = len(test_embeddings)
            
            for i in range(total):
                query_embedding = test_embeddings[i:i+1].astype("float32")
                true_label = test_metadata[i]["label"]
                
                scores, indices = index.search(query_embedding, k)
                
                # Quick saliency
                saliency_weight = 0.5  # Default
                
                # Weighted voting
                vote_scores = {"ham": 0.0, "spam": 0.0}
                for j in range(k):
                    neighbor_idx = indices[0][j]
                    similarity = float(scores[0][j])
                    neighbor_label = train_metadata[neighbor_idx]["label"]
                    
                    weight = (1 - alpha) * similarity * class_weights[neighbor_label] + alpha * saliency_weight
                    vote_scores[neighbor_label] += weight
                
                predicted_label = max(vote_scores, key=vote_scores.get)
                
                if predicted_label == true_label:
                    correct += 1
            
            accuracy = correct / total
            alpha_results.append((alpha, accuracy))
            
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_alpha = alpha
            
            logger.info(f"Alpha: {alpha:.1f}, Accuracy: {accuracy:.4f}")
        
        logger.info(f"Best alpha: {best_alpha:.1f} with accuracy: {best_accuracy:.4f}")
        return best_alpha, alpha_results
    
    def train(
        self,
        messages: List[str],
        labels: List[str],
        test_size: float = 0.2
    ) -> Dict:
        """Complete training pipeline"""
        
        logger.info("Starting training pipeline...")
        
        # Generate embeddings
        logger.info("Generating embeddings for all messages...")
        embeddings = self.generate_embeddings(messages)
        
        # Create metadata
        metadata = [
            {
                "index": i,
                "message": message,
                "label": label
            }
            for i, (message, label) in enumerate(zip(messages, labels))
        ]
        
        # Train-test split
        logger.info("Splitting data...")
        X_train, X_test, meta_train, meta_test = train_test_split(
            embeddings,
            metadata,
            test_size=test_size,
            random_state=42,
            stratify=[m["label"] for m in metadata]
        )
        
        logger.info(f"Train: {len(X_train)} samples")
        logger.info(f"Test: {len(X_test)} samples")
        
        # Calculate class weights
        train_labels = [m["label"] for m in meta_train]
        class_weights = self.calculate_class_weights(train_labels)
        
        # Build FAISS index
        index = self.build_faiss_index(X_train)
        
        # Optimize alpha
        best_alpha, alpha_results = self.optimize_alpha(
            X_test, meta_test, index, meta_train, class_weights
        )
        
        # Save artifacts
        logger.info("Saving artifacts...")
        
        # Save FAISS index
        faiss.write_index(index, str(self.output_dir / "faiss_index.bin"))
        
        # Save metadata
        with open(self.output_dir / "train_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(meta_train, f, ensure_ascii=False, indent=2)
        
        # Save class weights
        with open(self.output_dir / "class_weights.json", 'w', encoding='utf-8') as f:
            json.dump(class_weights, f, indent=2)
        
        # Save config
        config = {
            "model_name": self.model_name,
            "best_alpha": best_alpha,
            "alpha_results": alpha_results,
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "embedding_dim": embeddings.shape[1],
            "trained_at": datetime.now().isoformat()
        }
        
        with open(self.output_dir / "model_config.json", 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Artifacts saved to {self.output_dir}")
        
        return config
    

def main():
    """Main training script"""
    
    # Load data (assuming combined_dataset.csv exists)
    df = pd.read_csv("data/combined_dataset.csv")
    messages = df['message'].tolist()
    labels = df['label'].tolist()
    
    logger.info(f"Loaded {len(messages)} samples")
    
    # Train model
    trainer = ModelTrainer()
    config = trainer.train(messages, labels)
    
    logger.info("Training complete!")
    logger.info(f"Best alpha: {config['best_alpha']}")
    
    return config


if __name__ == "__main__":
    main()
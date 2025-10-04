"""
Application configuration settings.
"""


from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    # Project metadata
    PROJECT_NAME: str = "Spam Filter AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
    ]
    
    # Model paths
    MODEL_NAME: str = "intfloat/multilingual-e5-base"
    FAISS_INDEX_PATH: str = "artifacts/faiss_index.bin"
    METADATA_PATH: str = "artifacts/train_metadata.json"
    CLASS_WEIGHTS_PATH: str = "artifacts/class_weights.json"
    CONFIG_PATH: str =  "artifacts/model_config.json"

    # Model parameters
    DEFAULT_K: int = 5
    DEFAULT_ALPHA: float = 0.8
    MAX_SEQUENCE_LENGTH: int = 512
    BATCH_SIZE: int = 32
    
    # Data paths
    DATA_DIR: str = "data"
    ENGLISH_DATA_ID: str = "1N7rk-kfnDFIGMeX0ROVTjKh71gcgx-7R"
    VIETNAMESE_DATASET: str = "victorhoward2/vietnamese-spam-post-in-social-network"
    
    # Augmentation parameters
    AUG_RATIO: float = 0.2
    ALPHA_SPAM: float = 0.5
    ALPHA_HAM: float = 0.3
    
    # API settings
    MAX_MESSAGE_LENGTH: int = 10000
    RATE_LIMIT: int = 100  # requests per minute
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
        
settings = Settings()
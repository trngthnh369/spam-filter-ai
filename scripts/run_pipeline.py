"""
Complete end-to-end pipeline
Loads data, augments, trains model, and saves artifacts
"""

import sys
from pathlib import Path
import logging
import argparse

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from data_loader import DataLoader
from augmentation import DataAugmentor
from train_model import ModelTrainer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get project root directory (parent of scripts/)
PROJECT_ROOT = Path(__file__).parent.parent
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
DATA_DIR = PROJECT_ROOT / "data"


def run_complete_pipeline(
    use_augmentation: bool = True,
    test_size: float = 0.2,
    aug_ratio: float = 0.2,
    alpha: float = 0.3
):
    """Run complete data processing and training pipeline"""
    
    logger.info("="*60)
    logger.info("STARTING COMPLETE PIPELINE")
    logger.info("="*60)
    
    # Step 1: Load data
    logger.info("\n[STEP 1] Loading datasets...")
    loader = DataLoader(data_dir=str(DATA_DIR))
    
    try:
        df_english = loader.load_english_data()
        english_messages, english_labels = loader.preprocess_dataframe(df_english)
    except Exception as e:
        logger.error(f"Failed to load English data: {e}")
        return
    
    try:
        df_vietnamese = loader.load_vietnamese_data()
        vietnamese_messages, vietnamese_labels = loader.preprocess_dataframe(df_vietnamese)
    except Exception as e:
        logger.warning(f"Failed to load Vietnamese data: {e}")
        vietnamese_messages, vietnamese_labels = [], []
    
    # Combine datasets
    all_messages, all_labels = loader.combine_datasets(
        english_messages, english_labels,
        vietnamese_messages, vietnamese_labels
    )
    
    # Save combined data
    loader.save_combined_data(all_messages, all_labels)
    
    # Step 2: Data augmentation
    if use_augmentation:
        logger.info("\n[STEP 2] Augmenting data...")
        augmentor = DataAugmentor(data_dir=str(DATA_DIR))
        
        aug_messages, aug_labels = augmentor.augment_dataset(
            all_messages, all_labels,
            aug_ratio=aug_ratio,
            alpha=alpha
        )
        
        # Combine original + augmented
        original_count = len(all_messages)
        all_messages.extend(aug_messages)
        all_labels.extend(aug_labels)
        
        logger.info(f"Dataset expanded: {original_count} → {len(all_messages)} samples")
    else:
        logger.info("\n[STEP 2] Skipping augmentation...")
    
    # Step 3: Train model
    logger.info("\n[STEP 3] Training model...")
    trainer = ModelTrainer(output_dir=str(ARTIFACTS_DIR))
    config = trainer.train(all_messages, all_labels, test_size=test_size)
    
    # Step 4: Summary
    logger.info("\n" + "="*60)
    logger.info("PIPELINE COMPLETE!")
    logger.info("="*60)
    logger.info(f"Total samples: {len(all_messages)}")
    logger.info(f"Train samples: {config['train_samples']}")
    logger.info(f"Test samples: {config['test_samples']}")
    logger.info(f"Best alpha: {config['best_alpha']:.2f}")
    logger.info(f"Artifacts saved to: {ARTIFACTS_DIR}/")
    logger.info("="*60)
    
    return config


def main():
    parser = argparse.ArgumentParser(description="Run complete spam filter training pipeline")
    parser.add_argument("--no-augmentation", action="store_true", help="Skip data augmentation")
    parser.add_argument("--test-size", type=float, default=0.2, help="Test set ratio")
    parser.add_argument("--aug-ratio", type=float, default=0.2, help="Augmentation ratio")
    parser.add_argument("--alpha", type=float, default=0.3, help="Hard example generation alpha")
    
    args = parser.parse_args()
    
    config = run_complete_pipeline(
        use_augmentation=not args.no_augmentation,
        test_size=args.test_size,
        aug_ratio=args.aug_ratio,
        alpha=args.alpha
    )
    
    return config


if __name__ == "__main__":
    main()
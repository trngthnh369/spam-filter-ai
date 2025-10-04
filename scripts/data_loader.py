"""
Data loading and preprocessing script
Loads data from Google Drive and Kaggle, combines and preprocesses
"""

import pandas as pd
import gdown
import kagglehub
from kagglehub import KaggleDatasetAdapter
import logging
from pathlib import Path
from typing import Tuple, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    """Data loading utilities"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def load_english_data(self, file_id: str = "1N7rk-kfnDFIGMeX0ROVTjKh71gcgx-7R") -> pd.DataFrame:
        """Load English spam dataset from Google Drive"""
        logger.info(f"Loading English dataset from Google Drive (ID: {file_id})")
        
        output_path = self.data_dir / f"english_data_{file_id}.csv"
        
        # Download if not exists
        if not output_path.exists():
            gdown.download(
                f"https://drive.google.com/uc?id={file_id}",
                str(output_path),
                quiet=False
            )
        
        df = pd.read_csv(output_path)
        logger.info(f"Loaded {len(df)} English samples")
        logger.info(f"Columns: {list(df.columns)}")
        
        return df
    
    def load_vietnamese_data(self, dataset_name: str = "victorhoward2/vietnamese-spam-post-in-social-network") -> pd.DataFrame:
        """Load Vietnamese spam dataset from Kaggle"""
        logger.info(f"Loading Vietnamese dataset from Kaggle: {dataset_name}")
        
        df = kagglehub.load_dataset(
            KaggleDatasetAdapter.PANDAS,
            dataset_name,
            "vi_dataset.csv"
        )
        
        logger.info(f"Loaded {len(df)} Vietnamese samples")
        logger.info(f"Columns: {list(df.columns)}")
        
        return df
    
    def preprocess_dataframe(self, df: pd.DataFrame) -> Tuple[List[str], List[str]]:
        """
        Preprocess dataframe to extract messages and labels
        Handles various column name formats
        """
        logger.info("Preprocessing dataframe...")
        
        # Identify text column
        text_column = None
        text_candidates = ['message', 'text', 'content', 'email', 'post', 'comment', 'texts_vi', 'Message']
        for col in df.columns:
            if col in text_candidates or 'text' in col.lower() or 'message' in col.lower():
                text_column = col
                break
        
        if text_column is None:
            text_column = df.columns[0]
            logger.warning(f"Text column not found, using first column: {text_column}")
        
        # Identify label column
        label_column = None
        label_candidates = ['label', 'class', 'category', 'type', 'Category']
        for col in df.columns:
            if col in label_candidates or 'label' in col.lower():
                label_column = col
                break
        
        if label_column is None:
            label_column = df.columns[1] if len(df.columns) > 1 else df.columns[0]
            logger.warning(f"Label column not found, using: {label_column}")
        
        logger.info(f"Using text column: {text_column}")
        logger.info(f"Using label column: {label_column}")
        
        # Clean text data
        df[text_column] = df[text_column].astype(str).fillna('')
        df = df[df[text_column].str.strip() != '']
        
        # Clean labels - convert to ham/spam
        df[label_column] = df[label_column].astype(str).str.lower()
        
        label_mapping = {
            '0': 'ham', '1': 'spam',
            'ham': 'ham', 'spam': 'spam',
            'normal': 'ham', 'spam': 'spam',
            'legitimate': 'ham', 'phishing': 'spam',
            'not_spam': 'ham', 'is_spam': 'spam'
        }
        
        df[label_column] = df[label_column].map(label_mapping).fillna(df[label_column])
        
        # Show distribution
        label_counts = df[label_column].value_counts()
        logger.info(f"Label distribution:")
        for label, count in label_counts.items():
            logger.info(f"  {label}: {count} samples")
        
        messages = df[text_column].tolist()
        labels = df[label_column].tolist()
        
        logger.info(f"Preprocessed {len(messages)} messages")
        
        return messages, labels
    
    def combine_datasets(
        self,
        english_messages: List[str],
        english_labels: List[str],
        vietnamese_messages: List[str],
        vietnamese_labels: List[str]
    ) -> Tuple[List[str], List[str]]:
        """Combine English and Vietnamese datasets"""
        
        logger.info("Combining datasets...")
        
        all_messages = english_messages + vietnamese_messages
        all_labels = english_labels + vietnamese_labels
        
        logger.info(f"Combined dataset: {len(all_messages)} total samples")
        logger.info(f"  English: {len(english_messages)} samples")
        logger.info(f"  Vietnamese: {len(vietnamese_messages)} samples")
        
        # Show combined distribution
        from collections import Counter
        label_counts = Counter(all_labels)
        logger.info("Combined label distribution:")
        for label, count in label_counts.items():
            logger.info(f"  {label}: {count} samples ({count/len(all_labels)*100:.1f}%)")
        
        return all_messages, all_labels

    def save_combined_data(
        self,
        messages: List[str],
        labels: List[str],
        output_path: str = None
    ):
        """Save combined dataset to CSV"""
        
        if output_path is None:
            output_path = self.data_dir / "combined_dataset.csv"
        
        df = pd.DataFrame({
            'message': messages,
            'label': labels
        })
        
        df.to_csv(output_path, index=False, encoding='utf-8')
        logger.info(f"Saved combined dataset to {output_path}")
        
        return output_path
    

def main():
    """Main data loading pipeline"""
    
    loader = DataLoader(data_dir="data")
    
    # Load English data
    df_english = loader.load_english_data()
    english_messages, english_labels = loader.preprocess_dataframe(df_english)
    
    # Load Vietnamese data
    df_vietnamese = loader.load_vietnamese_data()
    vietnamese_messages, vietnamese_labels = loader.preprocess_dataframe(df_vietnamese)
    
    # Combine datasets
    all_messages, all_labels = loader.combine_datasets(
        english_messages, english_labels,
        vietnamese_messages, vietnamese_labels
    )
    
    # Save combined data
    output_path = loader.save_combined_data(all_messages, all_labels)
    
    logger.info(f"Data loading complete! Output: {output_path}")
    
    return all_messages, all_labels


if __name__ == "__main__":
    messages, labels = main()
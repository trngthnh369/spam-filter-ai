"""
Enhanced data augmentation module for spam classification
Includes hard example generation, synonym replacement, back-translation, and smart imbalance handling
"""

import pandas as pd
import random
import nltk
from typing import List, Tuple, Dict, Set
import logging
from collections import Counter
from pathlib import Path
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def detect_language(text: str) -> str:
    """
    Detect if text is Vietnamese or English
    Returns 'vi' for Vietnamese, 'en' for English
    """
    if not text or not isinstance(text, str):
        return 'en'
    
    # Vietnamese specific characters
    vietnamese_chars = 'àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ'
    vietnamese_chars += vietnamese_chars.upper()
    
    # Count Vietnamese characters
    vi_char_count = sum(1 for char in text if char in vietnamese_chars)
    
    # If more than 10% of characters are Vietnamese-specific, classify as Vietnamese
    total_alpha = sum(1 for char in text if char.isalpha())
    if total_alpha > 0 and (vi_char_count / total_alpha) > 0.1:
        return 'vi'
    
    return 'en'


def compute_text_similarity(text1: str, text2: str) -> float:
    """
    Compute simple similarity between two texts based on word overlap
    Returns similarity score between 0 and 1
    """
    if not text1 or not text2:
        return 0.0
    
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0

# Download NLTK data
try:
    from nltk.corpus import wordnet
    nltk.download('wordnet', quiet=True)
    nltk.download('omw-1.4', quiet=True)
    WORDNET_AVAILABLE = True
except:
    logger.warning("NLTK WordNet not available, synonym replacement disabled")
    WORDNET_AVAILABLE = False

    
class DataAugmentor:
    """Enhanced data augmentation for spam/ham classification with imbalance handling"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.spam_phrase_groups = self._init_spam_phrases()
        self.ham_phrase_groups = self._init_ham_phrases()
        self.spam_templates = self._init_spam_templates()
        
    def _init_spam_phrases(self) -> List[List[str]]:
        """Initialize spam phrase groups for hard example generation"""
        
        financial_phrases = [
            "you get $100 back", "they refund $200 instantly",
            "limited $50 bonus for early registration", "earn $150/day remote work",
            "approved for a $500 credit", "quick $300 refund if you confirm",
            "your account gets $100 instantly after confirmation",
            "instant $400 transfer if you reply YES today",
            "exclusive $600 grant approved for you",
            "claim your $1000 reward now", "receive $750 cashback immediately",
            "get $250 bonus for signing up", "win up to $5000 in prizes"
        ]
        
        promotion_phrases = [
            "limited time offer ends tonight", "buy one get one free today only",
            "exclusive deal just for you", "hot sale up to 80% off",
            "flash sale starting in 2 hours", "new collection, free shipping worldwide",
            "best price guaranteed for early birds", "special discount coupon",
            "reserve now and get extra 20% off", "only 3 items left, order now!",
            "70% OFF clearance sale", "mega discount today only",
            "last chance to save big", "don't miss out on this deal"
        ]
        
        lottery_phrases = [
            "congratulations! you've won a $1000 gift card",
            "you are selected to receive a free iPhone",
            "claim your $500 Amazon voucher now",
            "winner! reply to confirm your prize",
            "spin the wheel to win exciting gifts",
            "lucky draw winner – act fast",
            "you've been chosen for a special reward",
            "claim your free MacBook now"
        ]
        
        scam_alert_phrases = [
            "your account will be suspended unless verified",
            "unusual login detected, reset password now",
            "security update required immediately",
            "urgent: payment failed, update details now",
            "verify your identity to avoid account closure",
            "bank alert: confirm transaction or account locked",
            "suspicious activity detected on your account",
            "action required: verify within 24 hours"
        ]
        
        call_to_action_phrases = [
            "click here to confirm", "reply YES to activate bonus",
            "register before midnight and win", "tap now to claim your reward",
            "sign up today, limited seats", "confirm immediately to proceed",
            "act fast, offer expires soon", "click link to verify",
            "respond now to claim", "visit this link immediately"
        ]
        
        social_engineering_phrases = [
            "hey grandma, i need $500 for hospital bills",
            "hi mom, send money asap, phone broke",
            "boss asked me to buy 3 gift cards urgently",
            "john, can you transfer $300 now, emergency",
            "friend, please help me with $200 loan",
            "urgent family emergency, need cash now",
            "stranded abroad, need money for ticket home"
        ]
        
        obfuscated_phrases = [
            "Cl!ck h3re t0 w1n fr€e iPh0ne", "G€t y0ur r3fund n0w!!!",
            "L!mited 0ff3r: Fr33 $$$ r3ward", "C@shb@ck av@il@ble t0d@y",
            "W!n b!g pr!ze, act f@st", "FR€€ M0N€Y W@!T!NG",
            "V!@GR@ d!sc0unt 50% 0FF", "Earn $$$ from h0me"
        ]
        
        vietnamese_spam = [
            "trúng thưởng 10 triệu đồng", "khuyến mãi đặc biệt hôm nay",
            "nhận ngay 500k miễn phí", "cơ hội kiếm tiền dễ dàng",
            "giảm giá 80% chỉ hôm nay", "click vào link nhận quà",
            "xác nhận ngay để nhận thưởng", "ưu đãi độc quyền cho bạn"
        ]
        
        return [
            financial_phrases, promotion_phrases, lottery_phrases,
            scam_alert_phrases, call_to_action_phrases,
            social_engineering_phrases, obfuscated_phrases, vietnamese_spam
        ]
    
    def _init_ham_phrases(self) -> List[List[str]]:
        """Initialize ham phrase groups"""
        
        financial_phrases = [
            "I got $100 cashback yesterday", "The bank refunded me $200 already",
            "I earned $150/day last month from freelancing",
            "Got quick $300 refund after confirmation",
            "My account got $100 instantly after confirming",
            "I received instant $400 transfer today"
        ]
        
        promotion_phrases = [
            "I bought one and got one free, legit deal",
            "Flash sale 80% off, I already ordered",
            "Exclusive deal worked for me, saved a lot",
            "Got special coupon, it worked!",
            "Reserved early and saved 20%"
        ]
        
        return [financial_phrases, promotion_phrases]
    
    def _init_spam_templates(self) -> List[str]:
        """Templates for generating synthetic spam"""
        return [
            "URGENT: {action} to claim your {reward}!",
            "Congratulations! You've won {reward}. {action} now!",
            "LIMITED TIME: {reward} available. {action} immediately!",
            "{action} within 24 hours to receive {reward}",
            "ALERT: {action} required or your account will be {consequence}",
            "Special offer: {reward} if you {action} today!",
            "Don't miss out! {action} to get {reward}",
            "WINNER: You've been selected for {reward}. {action}!",
            "🎉 {reward} waiting for you! {action} to claim",
            "LAST CHANCE: {action} before midnight to get {reward}"
        ]
        
    def generate_synthetic_spam(self, n: int) -> List[str]:
        """Generate synthetic spam messages from templates"""
        
        actions = [
            "Click here", "Reply YES", "Confirm now", "Verify identity",
            "Call us", "Visit link", "Register", "Sign up", "Respond immediately",
            "Tap here", "Download app", "Enter details", "Update information"
        ]
        
        rewards = [
            "$1000 prize", "free iPhone", "cash reward", "$500 voucher",
            "exclusive gift", "special bonus", "luxury vacation", "cashback",
            "discount coupon", "free trial", "premium access", "winning ticket"
        ]
        
        consequences = [
            "suspended", "closed", "blocked", "restricted", "locked",
            "terminated", "deactivated", "frozen"
        ]
        
        generated = []
        for _ in range(n):
            template = random.choice(self.spam_templates)
            msg = template.format(
                action=random.choice(actions),
                reward=random.choice(rewards),
                consequence=random.choice(consequences)
            )
            generated.append(msg)
        
        return generated
    
    def generate_hard_examples(
        self,
        base_texts: List[str],
        phrase_groups: List[List[str]],
        n: int
    ) -> List[str]:
        """Generate hard examples by mixing base texts with phrases"""
        
        if not base_texts or n <= 0:
            return []
        
        generated = []
        for _ in range(n):
            try:
                base = random.choice(base_texts)
                insert_group = random.choice(phrase_groups)
                insert = random.choice(insert_group)
                
                # Different mixing strategies
                strategy = random.choice(['prefix', 'suffix', 'middle'])
                if strategy == 'prefix':
                    generated.append(f"{insert}. {base}")
                elif strategy == 'suffix':
                    generated.append(f"{base}. {insert}")
                else:
                    words = base.split()
                    mid = len(words) // 2
                    generated.append(f"{' '.join(words[:mid])} {insert} {' '.join(words[mid:])}")
                    
            except Exception as e:
                logger.warning(f"Error generating hard example: {e}")
                continue
        
        return generated
    
    def add_typos(self, text: str, typo_rate: float = 0.1) -> str:
        """Add realistic typos to text"""
        
        words = text.split()
        new_words = []
        
        for word in words:
            if random.random() < typo_rate and len(word) > 3:
                # Random typo strategies
                strategy = random.choice(['swap', 'delete', 'duplicate', 'replace'])
                word_list = list(word)
                
                if strategy == 'swap' and len(word_list) > 1:
                    i = random.randint(0, len(word_list) - 2)
                    word_list[i], word_list[i+1] = word_list[i+1], word_list[i]
                elif strategy == 'delete' and len(word_list) > 2:
                    i = random.randint(1, len(word_list) - 1)
                    word_list.pop(i)
                elif strategy == 'duplicate':
                    i = random.randint(0, len(word_list) - 1)
                    word_list.insert(i, word_list[i])
                elif strategy == 'replace':
                    i = random.randint(0, len(word_list) - 1)
                    neighbors = 'qwertyuiopasdfghjklzxcvbnm'
                    word_list[i] = random.choice(neighbors)
                
                word = ''.join(word_list)
            
            new_words.append(word)
        
        return ' '.join(new_words)
    
    def synonym_replacement(self, text: str, n: int = 1) -> str:
        """Replace words with synonyms using WordNet (English only)"""
        
        if not WORDNET_AVAILABLE:
            return text
        
        try:
            if isinstance(text, list):
                text = ' '.join(str(item) for item in text)
            elif not isinstance(text, str):
                text = str(text)
            
            if not text or not text.strip():
                return text
            
            # Only apply synonym replacement to English text
            if detect_language(text) != 'en':
                return text
            
            words = text.split()
            new_words = words.copy()
            
            # Find words with synonyms
            candidates = []
            for w in words:
                try:
                    if wordnet.synsets(w):
                        candidates.append(w)
                except:
                    continue
            
            if not candidates:
                return text
            
            random.shuffle(candidates)
            replaced_count = 0
            
            for random_word in candidates:
                try:
                    synonyms = wordnet.synsets(random_word)
                    if synonyms:
                        synonym = synonyms[0].lemmas()[0].name().replace('_', ' ')
                        if synonym.lower() != random_word.lower():
                            new_words = [synonym if w == random_word else w for w in new_words]
                            replaced_count += 1
                    if replaced_count >= n:
                        break
                except:
                    continue
            
            return " ".join(new_words)
            
        except Exception as e:
            logger.warning(f"Synonym replacement error: {e}")
            return str(text) if text else ""
    
    def remove_similar_messages(
        self,
        messages: List[str],
        labels: List[str],
        similarity_threshold: float = 0.85
    ) -> Tuple[List[str], List[str]]:
        """
        Remove duplicate and highly similar messages
        
        Args:
            messages: List of message texts
            labels: List of labels
            similarity_threshold: Threshold for similarity (0-1)
        
        Returns:
            filtered_messages, filtered_labels
        """
        
        logger.info(f"Removing similar messages (threshold: {similarity_threshold})...")
        
        filtered_messages = []
        filtered_labels = []
        seen_messages = set()
        
        for msg, label in zip(messages, labels):
            # Normalize message for comparison
            normalized_msg = msg.lower().strip()
            
            # Skip exact duplicates
            if normalized_msg in seen_messages:
                continue
            
            # Check similarity with existing messages
            is_similar = False
            for existing_msg in filtered_messages:
                similarity = compute_text_similarity(msg, existing_msg)
                if similarity >= similarity_threshold:
                    is_similar = True
                    break
            
            if not is_similar:
                filtered_messages.append(msg)
                filtered_labels.append(label)
                seen_messages.add(normalized_msg)
        
        removed_count = len(messages) - len(filtered_messages)
        logger.info(f"Removed {removed_count} similar messages ({removed_count/len(messages)*100:.1f}%)")
        logger.info(f"Remaining: {len(filtered_messages)} unique messages")
        
        return filtered_messages, filtered_labels
    
    def balance_dataset(
        self,
        messages: List[str],
        labels: List[str],
        target_ratio: float = 1.0
    ) -> Tuple[List[str], List[str]]:
        """
        Balance dataset by oversampling minority class
        
        Args:
            messages: List of message texts
            labels: List of labels
            target_ratio: Target spam/ham ratio (1.0 = equal)
        
        Returns:
            balanced_messages, balanced_labels
        """
        
        # Count distribution
        label_counts = Counter(labels)
        ham_count = label_counts.get('ham', 0)
        spam_count = label_counts.get('spam', 0)
        
        logger.info(f"Original distribution: Ham={ham_count}, Spam={spam_count}")
        
        # Determine minority class
        if ham_count == 0 or spam_count == 0:
            logger.warning("One class has 0 samples, cannot balance")
            return messages, labels
        
        # Calculate target counts
        if spam_count < ham_count:
            # Spam is minority
            target_spam = int(ham_count * target_ratio)
            needed = target_spam - spam_count
            minority_class = 'spam'
        else:
            # Ham is minority
            target_ham = int(spam_count / target_ratio)
            needed = target_ham - ham_count
            minority_class = 'ham'
        
        if needed <= 0:
            logger.info("Dataset already balanced")
            return messages, labels
        
        logger.info(f"Need to generate {needed} additional {minority_class} samples")
        
        # Collect minority samples
        minority_samples = [msg for msg, label in zip(messages, labels) if label == minority_class]
        
        augmented_messages = []
        augmented_labels = []
        
        if minority_class == 'spam':
            # Generate synthetic spam
            synthetic_count = min(needed // 3, 1000)
            synthetic_spam = self.generate_synthetic_spam(synthetic_count)
            augmented_messages.extend(synthetic_spam)
            augmented_labels.extend(['spam'] * len(synthetic_spam))
            needed -= len(synthetic_spam)
            logger.info(f"Generated {len(synthetic_spam)} synthetic spam messages")
            
            # Generate hard examples
            if needed > 0:
                hard_count = min(needed // 2, len(minority_samples) * 2)
                hard_spam = self.generate_hard_examples(
                    minority_samples, self.spam_phrase_groups, hard_count
                )
                augmented_messages.extend(hard_spam)
                augmented_labels.extend(['spam'] * len(hard_spam))
                needed -= len(hard_spam)
                logger.info(f"Generated {len(hard_spam)} hard spam examples")
        
        # Synonym replacement and typos for remaining (language-aware)
        if needed > 0:
            attempts = 0
            max_attempts = needed * 3
            
            while len(augmented_messages) < needed and attempts < max_attempts:
                original = random.choice(minority_samples)
                lang = detect_language(original)
                
                # Apply augmentation based on language
                if lang == 'en':
                    # For English: can use synonym replacement
                    aug_strategy = random.choice(['synonym', 'typo', 'both'])
                    
                    if aug_strategy == 'synonym':
                        augmented = self.synonym_replacement(original, n=2)
                    elif aug_strategy == 'typo':
                        augmented = self.add_typos(original, typo_rate=0.15)
                    else:
                        augmented = self.synonym_replacement(original, n=1)
                        augmented = self.add_typos(augmented, typo_rate=0.1)
                else:
                    # For Vietnamese: only use typos (no synonym replacement)
                    augmented = self.add_typos(original, typo_rate=0.15)
                
                # Check if different enough and not too similar to original
                similarity = compute_text_similarity(augmented, original)
                if (augmented != original and 
                    len(augmented.strip()) > 5 and 
                    similarity < 0.95):  # Not too similar to original
                    augmented_messages.append(augmented)
                    augmented_labels.append(minority_class)
                
                attempts += 1
            
            logger.info(f"Generated {len(augmented_messages)} language-aware augmented {minority_class} samples")
        
        return augmented_messages, augmented_labels
        
    def augment_dataset(
        self,
        messages: List[str],
        labels: List[str],
        aug_ratio: float = 0.2,
        alpha: float = 0.3,
        balance: bool = True,
        target_ratio: float = 0.8,
        output_path: str = None
    ) -> Tuple[List[str], List[str]]:
        """
        Complete data augmentation pipeline with smart balancing
        
        Args:
            messages: List of message texts
            labels: List of labels ('ham'/'spam')
            aug_ratio: Ratio for synonym replacement
            alpha: Ratio for hard example generation
            balance: Whether to balance the dataset
            target_ratio: Target spam/ham ratio (0.8 = spam:ham = 4:5)
        
        Returns:
            augmented_messages, augmented_labels
        """
        
        augmented_messages = []
        augmented_labels = []
        
        # Clean messages
        clean_messages = []
        for msg in messages:
            if isinstance(msg, list):
                clean_messages.append(' '.join(str(item) for item in msg))
            else:
                clean_messages.append(str(msg))
        
        messages = clean_messages
        
        # Count distribution
        label_counts = Counter(labels)
        ham_count = label_counts.get('ham', 0)
        spam_count = label_counts.get('spam', 0)
        
        logger.info(f"Original dataset: Ham={ham_count}, Spam={spam_count}, Ratio={spam_count/(ham_count+1):.2f}")
        
        # Step 1: Balance dataset if requested
        if balance:
            logger.info("Balancing dataset...")
            bal_messages, bal_labels = self.balance_dataset(messages, labels, target_ratio)
            augmented_messages.extend(bal_messages)
            augmented_labels.extend(bal_labels)
            
            new_counts = Counter(augmented_labels)
            logger.info(f"After balancing: Ham={new_counts.get('ham', 0)}, Spam={new_counts.get('spam', 0)}")
        
        # Step 2: Additional language-aware augmentation
        max_aug_syn = int(len(messages) * aug_ratio)
        logger.info(f"Generating up to {max_aug_syn} language-aware augmentations...")
        
        # Separate messages by language
        en_samples = [(msg, label) for msg, label in zip(messages, labels) if detect_language(msg) == 'en']
        vi_samples = [(msg, label) for msg, label in zip(messages, labels) if detect_language(msg) == 'vi']
        
        logger.info(f"Language distribution: English={len(en_samples)}, Vietnamese={len(vi_samples)}")
        
        syn_count = 0
        attempts = 0
        max_attempts = len(messages) * 2
        
        # Augment English messages
        for msg, label in en_samples:
            if syn_count >= max_aug_syn or attempts >= max_attempts:
                break
            
            attempts += 1
            
            if random.random() > 0.8:  # 20% chance
                try:
                    aug_msg = self.synonym_replacement(msg, n=1)
                    
                    similarity = compute_text_similarity(aug_msg, msg)
                    if (aug_msg != msg and
                        len(aug_msg.strip()) > 0 and
                        len(aug_msg.split()) >= 2 and
                        similarity < 0.95):
                        
                        augmented_messages.append(aug_msg)
                        augmented_labels.append(label)
                        syn_count += 1
                        
                except Exception as e:
                    logger.warning(f"Synonym replacement error: {e}")
                    continue
        
        # Augment Vietnamese messages (typos only)
        for msg, label in vi_samples:
            if syn_count >= max_aug_syn or attempts >= max_attempts:
                break
            
            attempts += 1
            
            if random.random() > 0.8:  # 20% chance
                try:
                    aug_msg = self.add_typos(msg, typo_rate=0.15)
                    
                    similarity = compute_text_similarity(aug_msg, msg)
                    if (aug_msg != msg and
                        len(aug_msg.strip()) > 0 and
                        len(aug_msg.split()) >= 2 and
                        similarity < 0.95):
                        
                        augmented_messages.append(aug_msg)
                        augmented_labels.append(label)
                        syn_count += 1
                        
                except Exception as e:
                    logger.warning(f"Typo augmentation error: {e}")
                    continue
        
        logger.info(f"Generated {syn_count} language-aware augmentation examples")
        
        # Step 3: Remove similar messages
        logger.info("Removing similar messages...")
        augmented_messages, augmented_labels = self.remove_similar_messages(
            augmented_messages, augmented_labels, similarity_threshold=0.85
        )
        
        final_counts = Counter(augmented_labels)
        logger.info(f"Final augmented dataset: Ham={final_counts.get('ham', 0)}, Spam={final_counts.get('spam', 0)}")
        logger.info(f"Total augmented: {len(augmented_messages)} examples")
        
        # Save augmented dataset
        if output_path is None:
            output_path = self.data_dir / "augmented_dataset.csv"
        
        df = pd.DataFrame({
            'message': augmented_messages,
            'label': augmented_labels
        })
        
        df.to_csv(output_path, index=False, encoding='utf-8')
        logger.info(f"Saved augmented dataset to {output_path}")
        
        return augmented_messages, augmented_labels


def main():
    """Example usage"""
    
    # Example data with imbalance
    messages = [
        "Hello, how are you?",
        "Meeting at 3pm tomorrow",
        "Thanks for the update",
        "Can we reschedule?",
        "Win free iPhone now!",
        "Click here for $1000 prize"
    ]
    labels = ['ham', 'ham', 'ham', 'ham', 'spam', 'spam']
    
    augmentor = DataAugmentor(data_dir="data")
    aug_messages, aug_labels = augmentor.augment_dataset(
        messages, labels, balance=True, target_ratio=0.8
    )
    
    logger.info(f"Original: {len(messages)} samples")
    logger.info(f"Augmented: {len(aug_messages)} samples")
    
    return aug_messages, aug_labels


if __name__ == "__main__":
    main()
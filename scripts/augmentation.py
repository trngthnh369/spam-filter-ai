"""
Data augmentation module for spam classification
Includes hard example generation and synonym replacement
"""

import random
import nltk
from typing import List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    """Data augmentation for spam/ham classification"""
    
    def __init__(self):
        self.spam_phrase_groups = self._init_spam_phrases()
        self.ham_phrase_groups = self._init_ham_phrases()
        
    def _init_spam_phrases(self) -> List[List[str]]:
        """Initialize spam phrase groups for hard example generation"""
        
        financial_phrases = [
            "you get $100 back", "they refund $200 instantly",
            "limited $50 bonus for early registration", "earn $150/day remote work",
            "approved for a $500 credit", "quick $300 refund if you confirm",
            "your account gets $100 instantly after confirmation",
            "instant $400 transfer if you reply YES today",
            "exclusive $600 grant approved for you"
        ]
        
        promotion_phrases = [
            "limited time offer ends tonight", "buy one get one free today only",
            "exclusive deal just for you", "hot sale up to 80% off",
            "flash sale starting in 2 hours", "new collection, free shipping worldwide",
            "best price guaranteed for early birds", "special discount coupon",
            "reserve now and get extra 20% off", "only 3 items left, order now!"
        ]
        
        lottery_phrases = [
            "congratulations! you've won a $1000 gift card",
            "you are selected to receive a free iPhone",
            "claim your $500 Amazon voucher now",
            "winner! reply to confirm your prize",
            "spin the wheel to win exciting gifts",
            "lucky draw winner – act fast"
        ]
        
        scam_alert_phrases = [
            "your account will be suspended unless verified",
            "unusual login detected, reset password now",
            "security update required immediately",
            "urgent: payment failed, update details now",
            "verify your identity to avoid account closure",
            "bank alert: confirm transaction or account locked"
        ]
        
        call_to_action_phrases = [
            "click here to confirm", "reply YES to activate bonus",
            "register before midnight and win", "tap now to claim your reward",
            "sign up today, limited seats", "confirm immediately to proceed",
            "act fast, offer expires soon"
        ]
        
        social_engineering_phrases = [
            "hey grandma, i need $500 for hospital bills",
            "hi mom, send money asap, phone broke",
            "boss asked me to buy 3 gift cards urgently",
            "john, can you transfer $300 now, emergency",
            "friend, please help me with $200 loan"
        ]
        
        obfuscated_phrases = [
            "Cl!ck h3re t0 w1n fr€e iPh0ne", "G€t y0ur r3fund n0w!!!",
            "L!mited 0ff3r: Fr33 $$$ r3ward", "C@shb@ck av@il@ble t0d@y",
            "W!n b!g pr!ze, act f@st"
        ]
        
        return [
            financial_phrases, promotion_phrases, lottery_phrases,
            scam_alert_phrases, call_to_action_phrases,
            social_engineering_phrases, obfuscated_phrases
        ]
    
    def _init_ham_phrases(self) -> List[List[str]]:
        """Initialize ham phrase groups (look like spam but legitimate)"""
        
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
        
        lottery_phrases = [
            "I actually won a $1000 voucher at the mall",
            "I got a free iPhone from the lucky draw",
            "Claimed my $500 Amazon voucher legit",
            "Won a prize, just showed my ticket"
        ]
        
        scam_alert_phrases = [
            "I got unusual login alert, but it was me",
            "Reset my password after warning, fine now",
            "Got security update mail, confirmed it's real",
            "Payment failed once, updated and ok now"
        ]
        
        call_to_action_phrases = [
            "I clicked to confirm and it worked",
            "Replied YES, bonus legit",
            "Registered before midnight, no scam",
            "Tapped link, claimed reward legit"
        ]
        
        social_engineering_phrases = [
            "Mom, don't worry I sent you $500 hospital bill already",
            "Hi mom, phone broke but friend helped",
            "Boss asked me to buy gift cards for office, already did",
            "John, I transferred $300, check it"
        ]
        
        obfuscated_phrases = [
            "Clicked h3re to win fr€e gift, real promo",
            "Got r3fund n0w!!! 100% legit",
            "Fr33 reward worked, tried it",
            "C@shb@ck real, used today"
        ]
        
        return [
            financial_phrases, promotion_phrases, lottery_phrases,
            scam_alert_phrases, call_to_action_phrases,
            social_engineering_phrases, obfuscated_phrases
        ]
        
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
                
                if random.random() > 0.5:
                    generated.append(f"{base}, btw {insert}.")
                else:
                    generated.append(f"{insert}. {base}")
            except Exception as e:
                logger.warning(f"Error generating hard example: {e}")
                continue
        
        return generated
    
    def synonym_replacement(self, text: str, n: int = 1) -> str:
        """Replace words with synonyms using WordNet"""
        
        if not WORDNET_AVAILABLE:
            return text
        
        try:
            if isinstance(text, list):
                text = ' '.join(str(item) for item in text)
            elif not isinstance(text, str):
                text = str(text)
            
            if not text or not text.strip():
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
        
    def augment_dataset(
        self,
        messages: List[str],
        labels: List[str],
        aug_ratio: float = 0.2,
        alpha: float = 0.3
    ) -> Tuple[List[str], List[str]]:
        """
        Complete data augmentation pipeline
        
        Args:
            messages: List of message texts
            labels: List of labels ('ham'/'spam')
            aug_ratio: Ratio for synonym replacement
            alpha: Ratio for hard example generation
        
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
        ham_count = labels.count('ham')
        spam_count = labels.count('spam')
        
        logger.info(f"Original dataset: Ham={ham_count}, Spam={spam_count}")
        
        # 1. Hard Ham Generation
        if ham_count >= spam_count:
            ham_messages = [msg for msg, label in zip(messages, labels) if label == 'ham']
            n_hard_ham = int((ham_count - spam_count) * alpha)
            
            if n_hard_ham > 0 and ham_messages:
                logger.info(f"Generating {n_hard_ham} hard ham examples...")
                hard_ham = self.generate_hard_examples(
                    ham_messages, self.ham_phrase_groups, n_hard_ham
                )
                
                if hard_ham:
                    augmented_messages.extend(hard_ham)
                    augmented_labels.extend(['ham'] * len(hard_ham))
                    logger.info(f"Generated {len(hard_ham)} hard ham examples")
        
        # 2. Synonym Replacement
        max_aug_syn = int(len(messages) * aug_ratio)
        logger.info(f"Generating up to {max_aug_syn} synonym replacements...")
        
        syn_count = 0
        attempts = 0
        max_attempts = len(messages) * 2
        
        for msg, label in zip(messages, labels):
            if syn_count >= max_aug_syn or attempts >= max_attempts:
                break
            
            attempts += 1
            
            if random.random() > 0.8:  # 20% chance
                try:
                    aug_msg = self.synonym_replacement(msg, n=1)
                    
                    if (aug_msg != msg and
                        len(aug_msg.strip()) > 0 and
                        len(aug_msg.split()) >= 2):
                        
                        augmented_messages.append(aug_msg)
                        augmented_labels.append(label)
                        syn_count += 1
                        
                except Exception as e:
                    logger.warning(f"Synonym replacement error: {e}")
                    continue
        
        logger.info(f"Generated {syn_count} synonym replacement examples")
        logger.info(f"Total augmented: {len(augmented_messages)} examples")
        
        return augmented_messages, augmented_labels
    
    # Save augmented dataset
    
    

def main():
    """Example usage"""
    
    # Example data
    messages = [
        "Hello, how are you?",
        "Win free iPhone now!",
        "Meeting at 3pm tomorrow",
        "Click here for $1000 prize"
    ]
    labels = ['ham', 'spam', 'ham', 'spam']
    
    augmentor = DataAugmentor()
    aug_messages, aug_labels = augmentor.augment_dataset(messages, labels)
    
    logger.info(f"Original: {len(messages)} samples")
    logger.info(f"Augmented: {len(aug_messages)} samples")
    
    return aug_messages, aug_labels


if __name__ == "__main__":
    main()
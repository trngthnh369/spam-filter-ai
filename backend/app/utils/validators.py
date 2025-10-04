"""
Custom validators
"""

from typing import Optional


def validate_message_length(message: str, max_length: int = 10000) -> bool:
    """Validate message length"""
    return 0 < len(message) <= max_length


def validate_k_parameter(k: int) -> bool:
    """Validate k parameter for KNN"""
    return 1 <= k <= 50


def validate_alpha_parameter(alpha: Optional[float]) -> bool:
    """Validate alpha parameter"""
    if alpha is None:
        return True
    return 0.0 <= alpha <= 1.0


def sanitize_message(message: str) -> str:
    """Sanitize message input"""
    # Remove any potential injection attempts
    message = message.replace('<script>', '').replace('</script>', '')
    message = message.replace('javascript:', '')
    return message.strip()

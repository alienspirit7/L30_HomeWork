"""
Hash Utilities

Provides hashing functions for ID generation and email anonymization.
"""

import hashlib
from typing import Union


def sha256_hash(value: str) -> str:
    """
    Generate SHA-256 hash of a string value.
    
    Args:
        value: String to hash
        
    Returns:
        Hexadecimal hash string
        
    Example:
        >>> sha256_hash("test@example.com")
        '973dfe463ec85785f5f95af5ba3906eedb2d931c24e69824a89ea65dba4e813b'
    """
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def generate_id(*components: Union[str, int]) -> str:
    """
    Generate a unique ID by hashing multiple components.
    
    Useful for creating deterministic IDs from multiple fields.
    
    Args:
        *components: Variable number of strings or integers to combine
        
    Returns:
        SHA-256 hash of the combined components
        
    Example:
        >>> generate_id("user@example.com", "2024-01-15", "subject")
        'a1b2c3...'
    """
    combined = '|'.join(str(c) for c in components)
    return sha256_hash(combined)

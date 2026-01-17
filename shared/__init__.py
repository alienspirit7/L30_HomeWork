"""
Shared Module - Centralized Library for BTS Architecture

Provides reusable components accessible by all modules:
- models: Data structures (EmailRecord, GradeRecord, FeedbackRecord, etc.)
- utils: Utilities (hashing, validation, file I/O, logging)
- interfaces: Abstract base classes for services and coordinators
- config: Configuration management
"""

__version__ = "1.0.0"
__author__ = "Homework Grading System"

from shared.models import EmailRecord, EmailStatus, GradeRecord, FeedbackRecord, StyleType
from shared.utils import sha256_hash, generate_id, validate_email, validate_github_url
from shared.interfaces import ServiceInterface, CoordinatorInterface

__all__ = [
    'EmailRecord', 'EmailStatus', 'GradeRecord', 'FeedbackRecord', 'StyleType',
    'sha256_hash', 'generate_id', 'validate_email', 'validate_github_url',
    'ServiceInterface', 'CoordinatorInterface',
]

"""
Draft Manager Module

A Level 2 task manager that orchestrates personalized email draft creation
by combining student identification with email composition.

This module coordinates two child services:
- Draft Composer: Creates Gmail drafts via Gmail API
- Student Mapper: Maps email addresses to student names

Usage:
    from draft_manager import DraftManager

    manager = DraftManager(config_path="./config.yaml")
    result = manager.process(input_data)
"""

__version__ = "1.0.0"
__author__ = "Draft Manager Team"
__level__ = 2

# Import main class for easy access
try:
    from .manager import DraftManager
    __all__ = ['DraftManager']
except ImportError:
    # manager.py might not exist yet
    __all__ = []

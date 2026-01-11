"""
Feedback Manager Service
Level 2 - Task Manager

Manages AI feedback generation: selecting feedback styles based on grades
and generating personalized feedback using Gemini API.
"""

from .service import FeedbackManager

__version__ = "1.0.0"
__all__ = ['FeedbackManager']

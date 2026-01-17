"""
Feedback Data Models

Data structures for AI-generated feedback throughout the BTS architecture.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class StyleType(Enum):
    """Feedback style based on grade range."""
    TRUMP = "trump"           # 90-100: enthusiastic, superlatives
    HASON = "hason"           # 70-89: witty, humorous
    CONSTRUCTIVE = "constructive"  # 55-69: constructive feedback
    AMSALEM = "amsalem"       # <55: brash, confrontational
    
    @classmethod
    def from_grade(cls, grade: float) -> 'StyleType':
        """Determine style based on grade value."""
        if grade >= 90:
            return cls.TRUMP
        elif grade >= 70:
            return cls.HASON
        elif grade >= 55:
            return cls.CONSTRUCTIVE
        else:
            return cls.AMSALEM


@dataclass
class FeedbackRecord:
    """
    Represents generated feedback for a student.
    
    Used by: feedback_manager, draft_manager, orchestrator
    Output file: file_3_4.xlsx
    """
    email_id: str                    # Matching email_id from previous files
    feedback: Optional[str]          # Generated feedback text (None if API fails)
    status: str                      # "Ready" or "Missing: reply"
    style: Optional[str] = None      # Style used for generation
    error: Optional[str] = None      # Error message if generation failed
    
    def is_ready(self) -> bool:
        """Check if feedback is ready for draft creation."""
        return self.status == "Ready" and self.feedback is not None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for Excel output."""
        return {
            'email_id': self.email_id,
            'reply': self.feedback,
            'status': self.status,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'FeedbackRecord':
        """Create FeedbackRecord from dictionary."""
        return cls(
            email_id=data.get('email_id', ''),
            feedback=data.get('reply') or data.get('feedback'),
            status=data.get('status', 'Missing: reply'),
            style=data.get('style'),
            error=data.get('error'),
        )

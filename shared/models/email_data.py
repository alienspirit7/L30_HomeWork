"""
Email Data Models

Data structures for email processing throughout the BTS architecture.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime


class EmailStatus(Enum):
    """Status of an email record."""
    READY = "Ready"
    MISSING_FIELDS = "Missing"
    ERROR = "Error"


@dataclass
class EmailRecord:
    """
    Represents a parsed email from Gmail.
    
    Used by: email_reader, draft_manager, orchestrator
    Output file: file_1_2.xlsx
    """
    email_id: str                    # SHA-256 hash identifier
    message_id: str                  # Gmail message ID (for reply threading)
    email_datetime: str              # Timestamp of email
    email_subject: str               # Email subject line
    repo_url: str                    # GitHub repository URL
    status: str                      # "Ready" or "Missing: [fields]"
    hashed_email_address: str        # SHA-256 of sender email
    sender_email: str                # Original sender email
    thread_id: str                   # Gmail thread ID
    
    def is_ready(self) -> bool:
        """Check if email record is ready for processing."""
        return self.status == EmailStatus.READY.value
    
    def to_dict(self) -> dict:
        """Convert to dictionary for Excel output."""
        return {
            'email_id': self.email_id,
            'message_id': self.message_id,
            'email_datetime': self.email_datetime,
            'email_subject': self.email_subject,
            'repo_url': self.repo_url,
            'status': self.status,
            'hashed_email_address': self.hashed_email_address,
            'sender_email': self.sender_email,
            'thread_id': self.thread_id,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'EmailRecord':
        """Create EmailRecord from dictionary."""
        return cls(
            email_id=data.get('email_id', ''),
            message_id=data.get('message_id', ''),
            email_datetime=data.get('email_datetime', ''),
            email_subject=data.get('email_subject', ''),
            repo_url=data.get('repo_url', ''),
            status=data.get('status', EmailStatus.MISSING_FIELDS.value),
            hashed_email_address=data.get('hashed_email_address', ''),
            sender_email=data.get('sender_email', ''),
            thread_id=data.get('thread_id', ''),
        )

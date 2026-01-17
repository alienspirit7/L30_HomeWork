"""
Student Data Models

Data structures for student information used in personalization.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class StudentRecord:
    """
    Represents a student from the mapping file.
    
    Used by: student_mapper, draft_manager
    Source file: students_mapping.xlsx
    """
    email_address: str               # Student email address
    name: str                        # Student name for personalization
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'email_address': self.email_address,
            'name': self.name,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'StudentRecord':
        """Create StudentRecord from dictionary."""
        return cls(
            email_address=data.get('email_address', ''),
            name=data.get('name', 'Student'),
        )

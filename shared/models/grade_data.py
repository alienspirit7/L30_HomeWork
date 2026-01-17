"""
Grade Data Models

Data structures for repository grading throughout the BTS architecture.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class AnalysisResult:
    """
    Result of Python code analysis.
    
    Used internally by python_analyzer and grade_manager.
    """
    lines_total: int                 # Total lines of code (excluding comments/blanks)
    lines_above_150: int             # Lines in files with >150 lines
    file_count: int                  # Number of Python files analyzed
    files_above_150: int = 0         # Number of files with >150 lines
    
    @property
    def grade(self) -> float:
        """Calculate grade based on lines ratio."""
        if self.lines_total == 0:
            return 0.0
        return (self.lines_above_150 / self.lines_total) * 100


@dataclass
class GradeRecord:
    """
    Represents a graded repository.
    
    Used by: grade_manager, feedback_manager, orchestrator
    Output file: file_2_3.xlsx
    """
    email_id: str                    # Matching email_id from file_1_2.xlsx
    grade: float                     # 0-100 calculated grade
    status: str                      # "Ready" or "Failed"
    error: Optional[str] = None      # Error message if status is "Failed"
    
    def is_ready(self) -> bool:
        """Check if grade record is ready for feedback generation."""
        return self.status == "Ready"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for Excel output."""
        return {
            'email_id': self.email_id,
            'grade': self.grade,
            'status': self.status,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GradeRecord':
        """Create GradeRecord from dictionary."""
        return cls(
            email_id=data.get('email_id', ''),
            grade=float(data.get('grade', 0)),
            status=data.get('status', 'Failed'),
            error=data.get('error'),
        )

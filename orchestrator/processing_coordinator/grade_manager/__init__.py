"""
Grade Manager Service
Orchestrates repository grading by cloning GitHub repositories and analyzing Python code.
"""

__version__ = "1.0.0"
__author__ = "Grade Manager Team"

from grade_manager.service import GradeManagerService

__all__ = ['GradeManagerService']

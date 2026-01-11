"""
Student Mapper Service Package

A service for mapping email addresses to student names using an Excel lookup table.
"""
from .student_mapper import StudentMapper, lookup_student

__version__ = "1.0.0"
__all__ = ['StudentMapper', 'lookup_student']

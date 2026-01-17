"""Shared Data Models Package"""

from shared.models.email_data import EmailRecord, EmailStatus
from shared.models.grade_data import GradeRecord, AnalysisResult
from shared.models.feedback_data import FeedbackRecord, StyleType
from shared.models.student_data import StudentRecord

__all__ = [
    'EmailRecord', 'EmailStatus',
    'GradeRecord', 'AnalysisResult',
    'FeedbackRecord', 'StyleType',
    'StudentRecord',
]

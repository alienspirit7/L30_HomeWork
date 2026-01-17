"""
Tests for Shared Models
"""

import pytest
from shared.models.email_data import EmailRecord, EmailStatus
from shared.models.grade_data import GradeRecord, AnalysisResult
from shared.models.feedback_data import FeedbackRecord, StyleType
from shared.models.student_data import StudentRecord


class TestEmailData:
    """Tests for email data models."""
    
    def test_email_status_values(self):
        """Test EmailStatus enum values."""
        assert EmailStatus.READY.value == "Ready"
        assert EmailStatus.MISSING_FIELDS.value == "Missing"
        assert EmailStatus.ERROR.value == "Error"
    
    def test_email_record_creation(self):
        """Test EmailRecord dataclass creation."""
        record = EmailRecord(
            email_id="abc123",
            message_id="msg123",
            email_datetime="2024-01-15",
            email_subject="Self check of homework 1",
            repo_url="https://github.com/user/repo.git",
            status="Ready",
            hashed_email_address="hashed123",
            sender_email="test@example.com",
            thread_id="thread123"
        )
        
        assert record.email_id == "abc123"
        assert record.is_ready() == True
    
    def test_email_record_not_ready(self):
        """Test EmailRecord is_ready returns False for non-Ready status."""
        record = EmailRecord(
            email_id="abc123",
            message_id="msg123",
            email_datetime="2024-01-15",
            email_subject="Test",
            repo_url="",
            status="Missing: repo_url",
            hashed_email_address="hashed123",
            sender_email="test@example.com",
            thread_id="thread123"
        )
        
        assert record.is_ready() == False
    
    def test_email_record_to_dict(self):
        """Test EmailRecord to_dict method."""
        record = EmailRecord(
            email_id="abc123",
            message_id="msg123",
            email_datetime="2024-01-15",
            email_subject="Test",
            repo_url="https://github.com/user/repo.git",
            status="Ready",
            hashed_email_address="hashed123",
            sender_email="test@example.com",
            thread_id="thread123"
        )
        
        d = record.to_dict()
        
        assert d['email_id'] == "abc123"
        assert d['repo_url'] == "https://github.com/user/repo.git"
    
    def test_email_record_from_dict(self):
        """Test EmailRecord from_dict class method."""
        data = {
            'email_id': 'abc123',
            'message_id': 'msg123',
            'email_datetime': '2024-01-15',
            'email_subject': 'Test',
            'repo_url': 'https://github.com/user/repo.git',
            'status': 'Ready',
            'hashed_email_address': 'hashed123',
            'sender_email': 'test@example.com',
            'thread_id': 'thread123'
        }
        
        record = EmailRecord.from_dict(data)
        
        assert record.email_id == 'abc123'
        assert record.is_ready() == True


class TestGradeData:
    """Tests for grade data models."""
    
    def test_analysis_result_grade_calculation(self):
        """Test AnalysisResult grade property calculation."""
        result = AnalysisResult(
            lines_total=1000,
            lines_above_150=800,
            file_count=10
        )
        
        assert result.grade == 80.0
    
    def test_analysis_result_zero_lines(self):
        """Test AnalysisResult with zero lines returns 0 grade."""
        result = AnalysisResult(
            lines_total=0,
            lines_above_150=0,
            file_count=0
        )
        
        assert result.grade == 0.0
    
    def test_grade_record_creation(self):
        """Test GradeRecord dataclass creation."""
        record = GradeRecord(
            email_id="abc123",
            grade=85.5,
            status="Ready"
        )
        
        assert record.email_id == "abc123"
        assert record.grade == 85.5
        assert record.is_ready() == True
    
    def test_grade_record_to_dict(self):
        """Test GradeRecord to_dict method."""
        record = GradeRecord(
            email_id="abc123",
            grade=85.5,
            status="Ready"
        )
        
        d = record.to_dict()
        
        assert d['email_id'] == "abc123"
        assert d['grade'] == 85.5
        assert d['status'] == "Ready"


class TestFeedbackData:
    """Tests for feedback data models."""
    
    def test_style_type_from_grade_trump(self):
        """Test StyleType.from_grade returns TRUMP for 90+."""
        assert StyleType.from_grade(95) == StyleType.TRUMP
        assert StyleType.from_grade(90) == StyleType.TRUMP
    
    def test_style_type_from_grade_hason(self):
        """Test StyleType.from_grade returns HASON for 70-89."""
        assert StyleType.from_grade(85) == StyleType.HASON
        assert StyleType.from_grade(70) == StyleType.HASON
    
    def test_style_type_from_grade_constructive(self):
        """Test StyleType.from_grade returns CONSTRUCTIVE for 55-69."""
        assert StyleType.from_grade(60) == StyleType.CONSTRUCTIVE
        assert StyleType.from_grade(55) == StyleType.CONSTRUCTIVE
    
    def test_style_type_from_grade_amsalem(self):
        """Test StyleType.from_grade returns AMSALEM for <55."""
        assert StyleType.from_grade(50) == StyleType.AMSALEM
        assert StyleType.from_grade(0) == StyleType.AMSALEM
    
    def test_feedback_record_is_ready(self):
        """Test FeedbackRecord is_ready method."""
        record = FeedbackRecord(
            email_id="abc123",
            feedback="Great work!",
            status="Ready"
        )
        
        assert record.is_ready() == True
    
    def test_feedback_record_not_ready(self):
        """Test FeedbackRecord is_ready returns False for missing feedback."""
        record = FeedbackRecord(
            email_id="abc123",
            feedback=None,
            status="Missing: reply"
        )
        
        assert record.is_ready() == False


class TestStudentData:
    """Tests for student data models."""
    
    def test_student_record_creation(self):
        """Test StudentRecord dataclass creation."""
        record = StudentRecord(
            email_address="student@example.com",
            name="John Doe"
        )
        
        assert record.email_address == "student@example.com"
        assert record.name == "John Doe"
    
    def test_student_record_to_dict(self):
        """Test StudentRecord to_dict method."""
        record = StudentRecord(
            email_address="student@example.com",
            name="John Doe"
        )
        
        d = record.to_dict()
        
        assert d['email_address'] == "student@example.com"
        assert d['name'] == "John Doe"

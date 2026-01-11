"""
Tests for Feedback Manager service.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from service import FeedbackManager


class TestFeedbackManager:
    """Test suite for FeedbackManager class."""

    @pytest.fixture
    def config_path(self, tmp_path):
        """Create a temporary config file."""
        config_content = """
manager:
  name: feedback_manager
  version: "1.0.0"

children:
  style_selector: "./style_selector"
  gemini_generator: "./gemini_generator"

input:
  file_path: "../grade_manager/data/output/file_2_3.xlsx"
  columns:
    email_id: "email_id"
    grade: "grade"
    status: "status"

output:
  file_path: "./data/output/file_3_4.xlsx"
  columns:
    email_id: "email_id"
    reply: "reply"
    status: "status"

rate_limiting:
  delay_between_calls_seconds: 0

logging:
  level: INFO
  file: "./logs/feedback_manager.log"
  console: false
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        return str(config_file)

    @patch('service.StyleSelector')
    @patch('service.GeminiGeneratorService')
    def test_initialization(self, mock_gemini, mock_style, config_path):
        """Test service initialization."""
        manager = FeedbackManager(config_path=config_path)

        assert manager.config is not None
        assert manager.logger is not None
        assert manager.config['manager']['name'] == 'feedback_manager'

    @patch('service.StyleSelector')
    @patch('service.GeminiGeneratorService')
    def test_health_check(self, mock_gemini, mock_style, config_path):
        """Test health check functionality."""
        # Setup mocks
        mock_style_instance = Mock()
        mock_style_instance.select_style.return_value = {'style_name': 'hason'}
        mock_style.return_value = mock_style_instance

        mock_gemini_instance = Mock()
        mock_gemini_instance.model = 'gemini-pro'
        mock_gemini.return_value = mock_gemini_instance

        manager = FeedbackManager(config_path=config_path)
        health = manager.health_check()

        assert 'feedback_manager' in health
        assert 'style_selector' in health
        assert 'gemini_generator' in health
        assert health['feedback_manager'] == 'OK'

    @patch('service.StyleSelector')
    @patch('service.GeminiGeneratorService')
    def test_generate_feedback_for_record_success(self, mock_gemini, mock_style, config_path):
        """Test successful feedback generation for a record."""
        # Setup mocks
        mock_style_instance = Mock()
        mock_style_instance.process.return_value = {
            'style_name': 'hason',
            'style_description': 'Witty style',
            'prompt_template': 'Generate witty feedback for grade 85'
        }
        mock_style.return_value = mock_style_instance

        mock_gemini_instance = Mock()
        mock_gemini_instance.process.return_value = {
            'feedback': 'Great work! Very funny code.',
            'status': 'Success',
            'error': None,
            'tokens_used': 50
        }
        mock_gemini.return_value = mock_gemini_instance

        manager = FeedbackManager(config_path=config_path)

        record = {
            'email_id': 'student@example.com',
            'grade': 85.0,
            'status': 'Ready'
        }

        result = manager._generate_feedback_for_record(record)

        assert result['email_id'] == 'student@example.com'
        assert result['reply'] == 'Great work! Very funny code.'
        assert result['status'] == 'Ready'

    @patch('service.StyleSelector')
    @patch('service.GeminiGeneratorService')
    def test_generate_feedback_for_record_failure(self, mock_gemini, mock_style, config_path):
        """Test failed feedback generation for a record."""
        # Setup mocks
        mock_style_instance = Mock()
        mock_style_instance.process.return_value = {
            'style_name': 'hason',
            'style_description': 'Witty style',
            'prompt_template': 'Generate witty feedback for grade 85'
        }
        mock_style.return_value = mock_style_instance

        mock_gemini_instance = Mock()
        mock_gemini_instance.process.return_value = {
            'feedback': None,
            'status': 'Failed',
            'error': 'API timeout',
            'tokens_used': 0
        }
        mock_gemini.return_value = mock_gemini_instance

        manager = FeedbackManager(config_path=config_path)

        record = {
            'email_id': 'student@example.com',
            'grade': 85.0,
            'status': 'Ready'
        }

        result = manager._generate_feedback_for_record(record)

        assert result['email_id'] == 'student@example.com'
        assert result['reply'] is None
        assert result['status'] == 'Missing: reply'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

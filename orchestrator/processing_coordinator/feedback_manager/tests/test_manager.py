"""
Tests for Feedback Manager service.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
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

    @patch('style_selector.service.StyleSelector')
    @patch('gemini_generator.service.GeminiGeneratorService')
    def test_initialization(self, mock_gemini, mock_style, config_path):
        """Test service initialization."""
        manager = FeedbackManager(config_path=config_path)

        assert manager.config is not None
        assert manager.logger is not None
        assert manager.config['manager']['name'] == 'feedback_manager'

    @patch('style_selector.service.StyleSelector')
    @patch('gemini_generator.service.GeminiGeneratorService')
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

    @patch('style_selector.service.StyleSelector')
    @patch('gemini_generator.service.GeminiGeneratorService')
    def test_generate_feedback_success(self, mock_gemini, mock_style, config_path):
        """Test successful feedback generation for a single record."""
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

        result = manager.generate_feedback(record)

        assert result['email_id'] == 'student@example.com'
        assert result['reply'] == 'Great work! Very funny code.'
        assert result['status'] == 'Ready'
        assert result['error'] is None

    @patch('style_selector.service.StyleSelector')
    @patch('gemini_generator.service.GeminiGeneratorService')
    def test_generate_feedback_failure(self, mock_gemini, mock_style, config_path):
        """Test failed feedback generation for a single record."""
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

        result = manager.generate_feedback(record)

        assert result['email_id'] == 'student@example.com'
        assert result['reply'] is None
        assert result['status'] == 'Missing: reply'
        assert result['error'] == 'API timeout'

    @patch('style_selector.service.StyleSelector')
    @patch('gemini_generator.service.GeminiGeneratorService')
    def test_process_multiple_records(self, mock_gemini, mock_style, config_path):
        """Test processing multiple grade records."""
        # Setup mocks
        mock_style_instance = Mock()
        mock_style_instance.process.return_value = {
            'style_name': 'hason',
            'style_description': 'Witty style',
            'prompt_template': 'Generate feedback'
        }
        mock_style.return_value = mock_style_instance

        # First call succeeds, second fails
        mock_gemini_instance = Mock()
        mock_gemini_instance.process.side_effect = [
            {'feedback': 'Great!', 'status': 'Success', 'error': None, 'tokens_used': 30},
            {'feedback': None, 'status': 'Failed', 'error': 'Timeout', 'tokens_used': 0}
        ]
        mock_gemini.return_value = mock_gemini_instance

        manager = FeedbackManager(config_path=config_path)

        records = [
            {'email_id': 'student1@example.com', 'grade': 90.0},
            {'email_id': 'student2@example.com', 'grade': 70.0}
        ]

        result = manager.process(records)

        assert len(result['feedback']) == 2
        assert result['generated_count'] == 1
        assert result['failed_count'] == 1
        assert result['feedback'][0]['status'] == 'Ready'
        assert result['feedback'][1]['status'] == 'Missing: reply'

    @patch('style_selector.service.StyleSelector')
    @patch('gemini_generator.service.GeminiGeneratorService')
    def test_process_empty_records(self, mock_gemini, mock_style, config_path):
        """Test processing with no records."""
        manager = FeedbackManager(config_path=config_path)

        result = manager.process([])

        assert result['feedback'] == []
        assert result['generated_count'] == 0
        assert result['failed_count'] == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

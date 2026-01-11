"""
Draft Manager Test Suite

Comprehensive tests for the Draft Manager module.
"""

import pytest
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from manager import DraftManager


class TestDraftManager:
    """Test cases for DraftManager class."""

    @pytest.fixture
    def sample_config(self, tmp_path):
        """Create a sample config file for testing."""
        config = {
            'manager': {
                'name': 'draft_manager',
                'version': '1.0.0'
            },
            'children': {
                'draft_composer': './draft_composer',
                'student_mapper': './student_mapper'
            },
            'email_template': {
                'greeting': 'Hi, {name}!',
                'signature': 'Thanks, Elena',
                'repo_line': 'Your code repository reviewed: {repo_url}'
            },
            'logging': {
                'level': 'INFO',
                'file': './logs/draft_manager.log'
            }
        }

        config_file = tmp_path / "config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)

        return str(config_file)

    @pytest.fixture
    def mock_child_services(self):
        """Mock the child services."""
        with patch('manager.StudentMapper') as mock_mapper, \
             patch('manager.DraftComposerService') as mock_composer:

            # Mock student mapper
            mock_mapper_instance = Mock()
            mock_mapper_instance.map_email_to_name.return_value = {
                'name': 'Alex Johnson',
                'found': True
            }
            mock_mapper_instance.get_stats.return_value = {
                'total_mappings': 8,
                'service': 'student_mapper',
                'version': '1.0.0'
            }
            mock_mapper.return_value = mock_mapper_instance

            # Mock draft composer
            mock_composer_instance = Mock()
            mock_composer_instance.process.return_value = {
                'draft_id': 'draft_xyz789',
                'status': 'Created',
                'error': None
            }
            mock_composer.return_value = mock_composer_instance

            yield {
                'mapper': mock_mapper_instance,
                'composer': mock_composer_instance
            }

    def test_initialization(self, sample_config, mock_child_services):
        """Test Draft Manager initialization."""
        manager = DraftManager(config_path=sample_config)

        assert manager.config['manager']['name'] == 'draft_manager'
        assert manager.config['manager']['version'] == '1.0.0'
        assert hasattr(manager, 'student_mapper')
        assert hasattr(manager, 'draft_composer')

    def test_load_config(self, sample_config):
        """Test configuration loading."""
        manager = DraftManager(config_path=sample_config)
        config = manager._load_config()

        assert 'manager' in config
        assert 'children' in config
        assert 'email_template' in config

    def test_compose_email_body(self, sample_config, mock_child_services):
        """Test email body composition."""
        manager = DraftManager(config_path=sample_config)

        body = manager._compose_email_body(
            name="Alex Johnson",
            feedback="Great work!",
            repo_url="https://github.com/student/repo"
        )

        assert "Hi, Alex Johnson!" in body
        assert "Great work!" in body
        assert "https://github.com/student/repo" in body
        assert "Thanks, Elena" in body

    def test_process_single_feedback_success(self, sample_config, mock_child_services):
        """Test processing a single feedback successfully."""
        manager = DraftManager(config_path=sample_config)

        feedback = {
            'email_id': 'msg_123',
            'feedback': 'Excellent work!',
            'status': 'Ready'
        }

        email_lookup = {
            'msg_123': {
                'email_id': 'msg_123',
                'sender_email': 'student1@example.com',
                'thread_id': 'thread_abc',
                'repo_url': 'https://github.com/student/repo',
                'subject': 'Homework Question'
            }
        }

        result = manager._process_single_feedback(feedback, email_lookup)

        assert result['status'] == 'Created'
        assert result['draft_id'] == 'draft_xyz789'
        assert result['email_id'] == 'msg_123'
        assert result['error'] is None

    def test_process_batch(self, sample_config, mock_child_services):
        """Test batch processing of multiple feedback records."""
        manager = DraftManager(config_path=sample_config)

        input_data = {
            'email_records': [
                {
                    'email_id': 'msg_001',
                    'sender_email': 'student1@example.com',
                    'thread_id': 'thread_abc',
                    'repo_url': 'https://github.com/student1/repo',
                    'subject': 'HW1'
                },
                {
                    'email_id': 'msg_002',
                    'sender_email': 'student2@example.com',
                    'thread_id': 'thread_def',
                    'repo_url': 'https://github.com/student2/repo',
                    'subject': 'HW1'
                }
            ],
            'feedback_records': [
                {
                    'email_id': 'msg_001',
                    'feedback': 'Great work!',
                    'status': 'Ready'
                },
                {
                    'email_id': 'msg_002',
                    'feedback': 'Good job!',
                    'status': 'Ready'
                }
            ]
        }

        result = manager.process(input_data)

        assert result['drafts_created'] == 2
        assert result['drafts_failed'] == 0
        assert len(result['draft_details']) == 2

    def test_skip_non_ready_feedback(self, sample_config, mock_child_services):
        """Test skipping feedback records that are not Ready."""
        manager = DraftManager(config_path=sample_config)

        input_data = {
            'email_records': [
                {
                    'email_id': 'msg_001',
                    'sender_email': 'student1@example.com',
                    'thread_id': 'thread_abc',
                    'repo_url': 'https://github.com/student1/repo'
                }
            ],
            'feedback_records': [
                {
                    'email_id': 'msg_001',
                    'feedback': 'Pending review',
                    'status': 'Pending'
                }
            ]
        }

        result = manager.process(input_data)

        assert result['drafts_created'] == 0
        assert result['drafts_failed'] == 0
        assert len(result['draft_details']) == 0

    def test_set_template(self, sample_config, mock_child_services):
        """Test custom template setting."""
        manager = DraftManager(config_path=sample_config)

        manager.set_template(
            greeting="Hello {name},",
            signature="Best regards, Dr. Smith"
        )

        assert manager.config['email_template']['greeting'] == "Hello {name},"
        assert manager.config['email_template']['signature'] == "Best regards, Dr. Smith"

    def test_get_stats(self, sample_config, mock_child_services):
        """Test getting manager statistics."""
        manager = DraftManager(config_path=sample_config)

        stats = manager.get_stats()

        assert stats['manager'] == 'draft_manager'
        assert stats['version'] == '1.0.0'
        assert stats['student_mappings'] == 8
        assert 'children' in stats

    def test_missing_email_record(self, sample_config, mock_child_services):
        """Test handling missing email record for feedback."""
        manager = DraftManager(config_path=sample_config)

        feedback = {
            'email_id': 'msg_999',
            'feedback': 'Test feedback',
            'status': 'Ready'
        }

        email_lookup = {}

        with pytest.raises(ValueError, match="No email record found"):
            manager._process_single_feedback(feedback, email_lookup)

    def test_process_single_convenience_method(self, sample_config, mock_child_services):
        """Test the process_single convenience method."""
        manager = DraftManager(config_path=sample_config)

        email_record = {
            'email_id': 'msg_123',
            'sender_email': 'student1@example.com',
            'thread_id': 'thread_abc',
            'repo_url': 'https://github.com/student/repo'
        }

        feedback_record = {
            'email_id': 'msg_123',
            'feedback': 'Great work!',
            'status': 'Ready'
        }

        result = manager.process_single(email_record, feedback_record)

        assert result['drafts_created'] == 1
        assert result['drafts_failed'] == 0


def test_main_function():
    """Test the main function runs without errors."""
    from manager import main
    # Just test that it doesn't raise an exception
    main()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

"""
Tests for Draft Composer Service
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import yaml
import os
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from service import DraftComposerService


class TestDraftComposerService(unittest.TestCase):
    """Test cases for DraftComposerService."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary config for testing
        self.test_config = {
            'service': {
                'name': 'draft_composer',
                'version': '1.0.0'
            },
            'gmail': {
                'credentials_path': './data/credentials/credentials.json',
                'token_path': './data/credentials/token.json',
                'scopes': ['https://www.googleapis.com/auth/gmail.compose']
            },
            'defaults': {
                'sender_name': 'Elena',
                'subject_prefix': 'Re: '
            },
            'logging': {
                'level': 'INFO',
                'file': './logs/draft_composer.log'
            }
        }

    @patch('service.yaml.safe_load')
    @patch('builtins.open')
    def test_load_config(self, mock_open, mock_yaml_load):
        """Test configuration loading."""
        mock_yaml_load.return_value = self.test_config

        service = DraftComposerService('./config.yaml')

        self.assertEqual(service.config['service']['name'], 'draft_composer')
        self.assertEqual(service.config['service']['version'], '1.0.0')

    @patch('service.yaml.safe_load')
    @patch('builtins.open')
    def test_process_success(self, mock_open, mock_yaml_load):
        """Test successful draft creation."""
        mock_yaml_load.return_value = self.test_config
        service = DraftComposerService('./config.yaml')

        # Mock Gmail service
        mock_gmail = MagicMock()
        mock_draft_response = {'id': 'draft_123456'}
        mock_gmail.users().drafts().create().execute.return_value = mock_draft_response
        service.gmail_service = mock_gmail

        # Test input
        input_data = {
            'to_email': 'student@example.com',
            'subject': 'Re: Homework Question',
            'body': 'Great work on the assignment!',
            'thread_id': 'thread_123',
            'in_reply_to': 'msg_456'
        }

        # Process
        result = service.process(input_data)

        # Assertions
        self.assertEqual(result['status'], 'Created')
        self.assertEqual(result['draft_id'], 'draft_123456')
        self.assertIsNone(result['error'])

    @patch('service.yaml.safe_load')
    @patch('builtins.open')
    def test_process_missing_field(self, mock_open, mock_yaml_load):
        """Test handling of missing required fields."""
        mock_yaml_load.return_value = self.test_config
        service = DraftComposerService('./config.yaml')

        # Test input missing 'body' field
        input_data = {
            'to_email': 'student@example.com',
            'subject': 'Re: Homework Question',
            'thread_id': 'thread_123',
            'in_reply_to': 'msg_456'
        }

        # Process
        result = service.process(input_data)

        # Assertions
        self.assertEqual(result['status'], 'Failed')
        self.assertIsNone(result['draft_id'])
        self.assertIsNotNone(result['error'])
        self.assertIn('Missing required input field', result['error'])

    @patch('service.yaml.safe_load')
    @patch('builtins.open')
    def test_create_draft_message(self, mock_open, mock_yaml_load):
        """Test draft message creation."""
        mock_yaml_load.return_value = self.test_config
        service = DraftComposerService('./config.yaml')

        draft_msg = service._create_draft_message(
            to='student@example.com',
            subject='Re: Test',
            body='Test body',
            thread_id='thread_123',
            in_reply_to='msg_456'
        )

        # Check structure
        self.assertIn('message', draft_msg)
        self.assertIn('raw', draft_msg['message'])
        self.assertIn('threadId', draft_msg['message'])
        self.assertEqual(draft_msg['message']['threadId'], 'thread_123')

    @patch('service.yaml.safe_load')
    @patch('builtins.open')
    @patch('service.build')
    def test_process_gmail_api_error(self, mock_build, mock_open, mock_yaml_load):
        """Test handling of Gmail API errors."""
        from googleapiclient.errors import HttpError

        mock_yaml_load.return_value = self.test_config
        service = DraftComposerService('./config.yaml')

        # Mock Gmail service to raise HttpError
        mock_gmail = MagicMock()
        mock_resp = Mock()
        mock_resp.status = 403
        mock_gmail.users().drafts().create().execute.side_effect = HttpError(
            mock_resp, b'Insufficient permissions'
        )
        service.gmail_service = mock_gmail

        input_data = {
            'to_email': 'student@example.com',
            'subject': 'Re: Test',
            'body': 'Test',
            'thread_id': 'thread_123',
            'in_reply_to': 'msg_456'
        }

        result = service.process(input_data)

        self.assertEqual(result['status'], 'Failed')
        self.assertIsNone(result['draft_id'])
        self.assertIsNotNone(result['error'])
        self.assertIn('Gmail API error', result['error'])


class TestDraftMessageFormat(unittest.TestCase):
    """Test draft message formatting."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_config = {
            'service': {'name': 'draft_composer', 'version': '1.0.0'},
            'gmail': {
                'credentials_path': './data/credentials/credentials.json',
                'token_path': './data/credentials/token.json',
                'scopes': ['https://www.googleapis.com/auth/gmail.compose']
            },
            'defaults': {'sender_name': 'Elena', 'subject_prefix': 'Re: '},
            'logging': {'level': 'INFO', 'file': './logs/draft_composer.log'}
        }

    @patch('service.yaml.safe_load')
    @patch('builtins.open')
    def test_message_includes_threading_headers(self, mock_open, mock_yaml_load):
        """Test that message includes proper threading headers."""
        import base64
        from email import message_from_bytes

        mock_yaml_load.return_value = self.test_config
        service = DraftComposerService('./config.yaml')

        draft_msg = service._create_draft_message(
            to='student@example.com',
            subject='Re: Test',
            body='Test body',
            thread_id='thread_123',
            in_reply_to='<msg_456@mail.gmail.com>'
        )

        # Decode the message
        raw_bytes = base64.urlsafe_b64decode(draft_msg['message']['raw'])
        parsed_msg = message_from_bytes(raw_bytes)

        # Check headers
        self.assertEqual(parsed_msg['To'], 'student@example.com')
        self.assertEqual(parsed_msg['Subject'], 'Re: Test')
        self.assertEqual(parsed_msg['In-Reply-To'], '<msg_456@mail.gmail.com>')
        self.assertEqual(parsed_msg['References'], '<msg_456@mail.gmail.com>')


if __name__ == '__main__':
    unittest.main()

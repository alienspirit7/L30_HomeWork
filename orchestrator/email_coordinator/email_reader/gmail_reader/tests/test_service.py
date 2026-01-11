"""Tests for Gmail Reader Service."""

import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from service import GmailReaderService


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    return {
        'service': {
            'name': 'gmail_reader',
            'version': '1.0.0'
        },
        'gmail': {
            'credentials_path': './data/credentials/credentials.json',
            'token_path': './data/credentials/token.json',
            'scopes': [
                'https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.modify'
            ]
        },
        'defaults': {
            'max_results': 100,
            'search_query': 'subject:(self check of homework) is:unread'
        },
        'logging': {
            'level': 'INFO',
            'file': './logs/gmail_reader.log'
        }
    }


@pytest.fixture
def mock_gmail_message():
    """Mock Gmail message for testing."""
    return {
        'id': 'msg123',
        'threadId': 'thread456',
        'internalDate': '1704067200000',  # 2024-01-01 00:00:00
        'snippet': 'This is a test email snippet...',
        'payload': {
            'headers': [
                {'name': 'From', 'value': 'student@example.com'},
                {'name': 'Subject', 'value': 'Self Check of Homework 5'},
                {'name': 'Date', 'value': 'Mon, 1 Jan 2024 00:00:00 +0000'}
            ],
            'body': {
                'data': 'VGhpcyBpcyB0aGUgZW1haWwgYm9keS4='  # "This is the email body."
            }
        }
    }


@pytest.fixture
def mock_gmail_multipart_message():
    """Mock Gmail multipart message for testing."""
    return {
        'id': 'msg789',
        'threadId': 'thread012',
        'internalDate': '1704153600000',  # 2024-01-02 00:00:00
        'snippet': 'Multipart email snippet...',
        'payload': {
            'headers': [
                {'name': 'From', 'value': 'student2@example.com'},
                {'name': 'Subject', 'value': 'SELF CHECK OF HOMEWORK 42'},
                {'name': 'Date', 'value': 'Tue, 2 Jan 2024 00:00:00 +0000'}
            ],
            'parts': [
                {
                    'mimeType': 'text/plain',
                    'body': {
                        'data': 'TXVsdGlwYXJ0IHBsYWluIHRleHQu'  # "Multipart plain text."
                    }
                },
                {
                    'mimeType': 'text/html',
                    'body': {
                        'data': 'PGh0bWw+TXVsdGlwYXJ0IEhUTUw8L2h0bWw+'
                    }
                }
            ]
        }
    }


class TestGmailReaderService:
    """Test cases for GmailReaderService."""

    @patch('service.yaml.safe_load')
    @patch('builtins.open')
    def test_init(self, mock_open, mock_yaml, mock_config):
        """Test service initialization."""
        mock_yaml.return_value = mock_config
        service = GmailReaderService()
        assert service.config == mock_config
        assert service.service is None

    @patch('service.yaml.safe_load')
    @patch('builtins.open')
    def test_load_config(self, mock_open, mock_yaml, mock_config):
        """Test configuration loading."""
        mock_yaml.return_value = mock_config
        service = GmailReaderService()
        assert service.config['service']['name'] == 'gmail_reader'
        assert 'gmail' in service.config
        assert 'defaults' in service.config

    @patch('service.yaml.safe_load')
    @patch('builtins.open')
    def test_decode_body_simple(self, mock_open, mock_yaml, mock_config, mock_gmail_message):
        """Test decoding simple message body."""
        mock_yaml.return_value = mock_config
        service = GmailReaderService()
        body = service._decode_body(mock_gmail_message)
        assert body == "This is the email body."

    @patch('service.yaml.safe_load')
    @patch('builtins.open')
    def test_decode_body_multipart(self, mock_open, mock_yaml, mock_config, mock_gmail_multipart_message):
        """Test decoding multipart message body."""
        mock_yaml.return_value = mock_config
        service = GmailReaderService()
        body = service._decode_body(mock_gmail_multipart_message)
        assert body == "Multipart plain text."

    @patch('service.yaml.safe_load')
    @patch('builtins.open')
    def test_get_header(self, mock_open, mock_yaml, mock_config, mock_gmail_message):
        """Test extracting header values."""
        mock_yaml.return_value = mock_config
        service = GmailReaderService()
        headers = mock_gmail_message['payload']['headers']

        sender = service._get_header(headers, 'From')
        assert sender == 'student@example.com'

        subject = service._get_header(headers, 'Subject')
        assert subject == 'Self Check of Homework 5'

        # Test case insensitive
        subject = service._get_header(headers, 'subject')
        assert subject == 'Self Check of Homework 5'

        # Test missing header
        missing = service._get_header(headers, 'NonExistent')
        assert missing == ''

    @patch('service.yaml.safe_load')
    @patch('builtins.open')
    def test_parse_email(self, mock_open, mock_yaml, mock_config, mock_gmail_message):
        """Test parsing Gmail message to standard format."""
        mock_yaml.return_value = mock_config
        service = GmailReaderService()
        parsed = service._parse_email(mock_gmail_message)

        assert parsed['message_id'] == 'msg123'
        assert parsed['thread_id'] == 'thread456'
        assert parsed['sender'] == 'student@example.com'
        assert parsed['subject'] == 'Self Check of Homework 5'
        assert parsed['body'] == 'This is the email body.'
        assert parsed['snippet'] == 'This is a test email snippet...'
        assert 'datetime' in parsed

    @patch('service.build')
    @patch('service.Credentials')
    @patch('os.path.exists')
    @patch('service.yaml.safe_load')
    @patch('builtins.open')
    def test_process_success(self, mock_open, mock_yaml, mock_exists, mock_creds, mock_build, mock_config, mock_gmail_message):
        """Test successful email processing."""
        mock_yaml.return_value = mock_config
        mock_exists.return_value = True

        # Mock credentials
        creds_mock = MagicMock()
        creds_mock.valid = True
        mock_creds.from_authorized_user_file.return_value = creds_mock

        # Mock Gmail API service
        service_mock = MagicMock()
        mock_build.return_value = service_mock

        # Mock messages list response
        list_response = {
            'messages': [
                {'id': 'msg123'}
            ]
        }
        service_mock.users().messages().list().execute.return_value = list_response

        # Mock message get response
        service_mock.users().messages().get().execute.return_value = mock_gmail_message

        # Create service and process
        service = GmailReaderService()
        input_data = {
            'search_query': 'subject:(self check of homework)',
            'max_results': 10,
            'mark_as_read': False
        }
        result = service.process(input_data)

        assert result['status'] == 'success'
        assert result['count'] == 1
        assert len(result['emails']) == 1
        assert result['emails'][0]['subject'] == 'Self Check of Homework 5'

    @patch('service.build')
    @patch('service.Credentials')
    @patch('os.path.exists')
    @patch('service.yaml.safe_load')
    @patch('builtins.open')
    def test_process_no_emails(self, mock_open, mock_yaml, mock_exists, mock_creds, mock_build, mock_config):
        """Test processing with no emails found."""
        mock_yaml.return_value = mock_config
        mock_exists.return_value = True

        # Mock credentials
        creds_mock = MagicMock()
        creds_mock.valid = True
        mock_creds.from_authorized_user_file.return_value = creds_mock

        # Mock Gmail API service
        service_mock = MagicMock()
        mock_build.return_value = service_mock

        # Mock empty messages list
        list_response = {'messages': []}
        service_mock.users().messages().list().execute.return_value = list_response

        # Create service and process
        service = GmailReaderService()
        input_data = {'search_query': 'subject:nonexistent'}
        result = service.process(input_data)

        assert result['status'] == 'success'
        assert result['count'] == 0
        assert len(result['emails']) == 0

    @patch('service.build')
    @patch('service.Credentials')
    @patch('os.path.exists')
    @patch('service.yaml.safe_load')
    @patch('builtins.open')
    def test_process_with_defaults(self, mock_open, mock_yaml, mock_exists, mock_creds, mock_build, mock_config):
        """Test processing with default parameters."""
        mock_yaml.return_value = mock_config
        mock_exists.return_value = True

        # Mock credentials
        creds_mock = MagicMock()
        creds_mock.valid = True
        mock_creds.from_authorized_user_file.return_value = creds_mock

        # Mock Gmail API service
        service_mock = MagicMock()
        mock_build.return_value = service_mock

        # Mock empty messages list
        list_response = {'messages': []}
        service_mock.users().messages().list().execute.return_value = list_response

        # Create service and process with empty input
        service = GmailReaderService()
        result = service.process({})

        assert result['status'] == 'success'
        # Verify default query was used
        call_args = service_mock.users().messages().list.call_args
        assert call_args[1]['q'] == mock_config['defaults']['search_query']
        assert call_args[1]['maxResults'] == mock_config['defaults']['max_results']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

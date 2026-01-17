"""
Test fixtures for Email Reader Manager tests
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock
import yaml


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def test_config(temp_dir):
    """Create a test configuration file."""
    config = {
        'manager': {
            'name': 'email_reader',
            'version': '1.0.0'
        },
        'children': {
            'gmail_reader': './gmail_reader',
            'email_parser': './email_parser'
        },
        'output': {
            'file_path': str(temp_dir / 'output' / 'file_1_2.xlsx'),
            'directory': str(temp_dir / 'output')
        },
        'modes': {
            'test': {'batch_size': 5},
            'batch': {'batch_size': 50},
            'full': {'batch_size': 1000}
        },
        'gmail_search': {
            'query': 'subject:(self check of homework) is:unread'
        },
        'logging': {
            'level': 'INFO',
            'file': str(temp_dir / 'logs' / 'email_reader.log'),
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    }

    config_path = temp_dir / 'config.yaml'
    with open(config_path, 'w') as f:
        yaml.dump(config, f)

    return str(config_path)


@pytest.fixture
def invalid_config(temp_dir):
    """Create an invalid configuration file."""
    config_path = temp_dir / 'invalid_config.yaml'
    with open(config_path, 'w') as f:
        f.write("invalid: yaml: content: [unclosed")

    return str(config_path)


@pytest.fixture
def sample_raw_emails():
    """Sample raw emails from Gmail Reader."""
    return [
        {
            'message_id': 'msg_001',
            'thread_id': 'thread_001',
            'sender': 'student1@example.com',
            'subject': 'Self check of homework 5',
            'body': 'Here is my homework: https://github.com/student1/homework-5',
            'datetime': '2026-01-15T10:00:00Z',
            'snippet': 'Here is my homework...'
        },
        {
            'message_id': 'msg_002',
            'thread_id': 'thread_002',
            'sender': 'student2@example.com',
            'subject': 'Self check of homework 10',
            'body': 'My repository: https://github.com/student2/hw-10.git',
            'datetime': '2026-01-15T11:00:00Z',
            'snippet': 'My repository...'
        },
        {
            'message_id': 'msg_003',
            'thread_id': 'thread_003',
            'sender': 'student3@example.com',
            'subject': 'Self check of homework 15',
            'body': 'No repository URL in this email',
            'datetime': '2026-01-15T12:00:00Z',
            'snippet': 'No repository...'
        }
    ]


@pytest.fixture
def sample_parsed_emails():
    """Sample parsed emails from Email Parser."""
    return [
        {
            'email_id': 'hash_001',
            'message_id': 'msg_001',
            'email_datetime': '2026-01-15T10:00:00Z',
            'email_subject': 'Self check of homework 5',
            'repo_url': 'https://github.com/student1/homework-5',
            'sender_email': 'student1@example.com',
            'hashed_email': 'hash_sender_001',
            'thread_id': 'thread_001',
            'status': 'Ready',
            'missing_fields': []
        },
        {
            'email_id': 'hash_002',
            'message_id': 'msg_002',
            'email_datetime': '2026-01-15T11:00:00Z',
            'email_subject': 'Self check of homework 10',
            'repo_url': 'https://github.com/student2/hw-10',
            'sender_email': 'student2@example.com',
            'hashed_email': 'hash_sender_002',
            'thread_id': 'thread_002',
            'status': 'Ready',
            'missing_fields': []
        },
        {
            'email_id': 'hash_003',
            'message_id': 'msg_003',
            'email_datetime': '2026-01-15T12:00:00Z',
            'email_subject': 'Self check of homework 15',
            'repo_url': None,
            'sender_email': 'student3@example.com',
            'hashed_email': 'hash_sender_003',
            'thread_id': 'thread_003',
            'status': 'Missing: repo_url',
            'missing_fields': ['repo_url']
        }
    ]


@pytest.fixture
def mock_gmail_reader():
    """Create a mock Gmail Reader service."""
    mock = Mock()
    mock.process = Mock()
    return mock


@pytest.fixture
def mock_email_parser():
    """Create a mock Email Parser service."""
    mock = Mock()
    mock.parse = Mock()
    return mock


@pytest.fixture
def gmail_reader_success_response(sample_raw_emails):
    """Gmail Reader successful response."""
    return {
        'emails': sample_raw_emails,
        'count': len(sample_raw_emails),
        'status': 'success'
    }


@pytest.fixture
def gmail_reader_failure_response():
    """Gmail Reader failure response."""
    return {
        'emails': [],
        'count': 0,
        'status': 'failed'
    }


@pytest.fixture
def gmail_reader_empty_response():
    """Gmail Reader empty response (no emails found)."""
    return {
        'emails': [],
        'count': 0,
        'status': 'success'
    }

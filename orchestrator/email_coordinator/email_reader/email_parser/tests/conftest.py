"""Pytest configuration and fixtures for email parser tests."""

import pytest
import tempfile
import yaml
from pathlib import Path


@pytest.fixture
def sample_config():
    """Provide sample configuration dictionary."""
    return {
        'service': {
            'name': 'email_parser',
            'version': '1.0.0'
        },
        'patterns': {
            'subject_pattern': r'self check of homework \d{1,3}',
            'github_patterns': [
                r'https://github.com/[\w-]+/[\w-]+(?:\.git)?',
                r'github.com/[\w-]+/[\w-]+'
            ]
        },
        'validation': {
            'required_fields': [
                'repo_url',
                'sender_email'
            ]
        },
        'logging': {
            'level': 'INFO',
            'file': './logs/email_parser.log'
        }
    }


@pytest.fixture
def config_file(sample_config, tmp_path):
    """Create a temporary config file."""
    config_path = tmp_path / "config.yaml"
    with open(config_path, 'w') as f:
        yaml.dump(sample_config, f)
    return str(config_path)


@pytest.fixture
def valid_raw_email():
    """Provide a valid raw email with all required fields."""
    return {
        'message_id': 'msg_12345abc',
        'thread_id': 'thread_67890def',
        'sender': 'student@example.com',
        'subject': 'Self check of homework 42',
        'body': 'Hi Professor,\n\nHere is my repository:\nhttps://github.com/student123/homework-42\n\nThanks!',
        'datetime': '2026-01-11T10:30:00Z'
    }


@pytest.fixture
def email_without_github():
    """Provide an email without GitHub URL."""
    return {
        'message_id': 'msg_test001',
        'thread_id': 'thread_test001',
        'sender': 'student@test.com',
        'subject': 'Self check of homework 1',
        'body': 'Hi, I completed the homework but forgot to include the link.',
        'datetime': '2026-01-11T09:00:00Z'
    }


@pytest.fixture
def email_invalid_subject():
    """Provide an email with invalid subject."""
    return {
        'message_id': 'msg_test002',
        'thread_id': 'thread_test002',
        'sender': 'student@test.com',
        'subject': 'Random subject line',
        'body': 'Repository: https://github.com/student/repo',
        'datetime': '2026-01-11T09:00:00Z'
    }


@pytest.fixture
def email_github_variations():
    """Provide emails with different GitHub URL formats."""
    return [
        {
            'message_id': 'msg_var1',
            'thread_id': 'thread_var1',
            'sender': 'test1@example.com',
            'subject': 'Self check of homework 10',
            'body': 'Repo: https://github.com/user/repo-name.git',
            'datetime': '2026-01-11T10:00:00Z'
        },
        {
            'message_id': 'msg_var2',
            'thread_id': 'thread_var2',
            'sender': 'test2@example.com',
            'subject': 'Self check of homework 11',
            'body': 'See: github.com/another-user/another-repo',
            'datetime': '2026-01-11T11:00:00Z'
        },
        {
            'message_id': 'msg_var3',
            'thread_id': 'thread_var3',
            'sender': 'test3@example.com',
            'subject': 'Self check of homework 12',
            'body': 'Link: https://github.com/my-user/my-repo',
            'datetime': '2026-01-11T12:00:00Z'
        }
    ]

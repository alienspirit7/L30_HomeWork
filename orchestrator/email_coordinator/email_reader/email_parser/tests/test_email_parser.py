"""Comprehensive tests for Email Parser Service."""

import pytest
import hashlib
from src.email_parser import EmailParser, create_parser


class TestEmailParserInitialization:
    """Tests for EmailParser initialization."""

    def test_parser_creation_with_valid_config(self, config_file):
        """Test creating parser with valid configuration."""
        parser = EmailParser(config_file)
        assert parser is not None
        assert parser.config['service']['name'] == 'email_parser'

    def test_parser_creation_with_missing_config(self):
        """Test creating parser with missing configuration file."""
        with pytest.raises(FileNotFoundError):
            EmailParser('nonexistent_config.yaml')

    def test_create_parser_factory(self, config_file):
        """Test factory function creates parser correctly."""
        parser = create_parser(config_file)
        assert isinstance(parser, EmailParser)


class TestHashGeneration:
    """Tests for hash generation functionality."""

    def test_generate_hash(self, config_file):
        """Test SHA-256 hash generation."""
        parser = EmailParser(config_file)
        test_data = "test@example.com"
        expected_hash = hashlib.sha256(test_data.encode('utf-8')).hexdigest()
        assert parser._generate_hash(test_data) == expected_hash

    def test_email_id_generation(self, config_file, valid_raw_email):
        """Test email ID is generated correctly."""
        parser = EmailParser(config_file)
        result = parser.parse(valid_raw_email)

        # Verify email_id is generated from sender:subject:datetime
        email_id_data = f"{valid_raw_email['sender']}:{valid_raw_email['subject']}:{valid_raw_email['datetime']}"
        expected_hash = hashlib.sha256(email_id_data.encode('utf-8')).hexdigest()

        assert result['email_id'] == expected_hash

    def test_hashed_email_generation(self, config_file, valid_raw_email):
        """Test sender email is hashed correctly."""
        parser = EmailParser(config_file)
        result = parser.parse(valid_raw_email)

        expected_hash = hashlib.sha256(valid_raw_email['sender'].encode('utf-8')).hexdigest()
        assert result['hashed_email'] == expected_hash


class TestGitHubURLExtraction:
    """Tests for GitHub URL extraction."""

    def test_extract_github_url_https_with_git(self, config_file):
        """Test extraction of HTTPS URL with .git suffix."""
        parser = EmailParser(config_file)
        body = "Repository: https://github.com/user/repo.git"
        url = parser._extract_github_url(body)
        assert url == "https://github.com/user/repo"

    def test_extract_github_url_https_without_git(self, config_file):
        """Test extraction of HTTPS URL without .git suffix."""
        parser = EmailParser(config_file)
        body = "Check out https://github.com/username/project-name"
        url = parser._extract_github_url(body)
        assert url == "https://github.com/username/project-name"

    def test_extract_github_url_without_protocol(self, config_file):
        """Test extraction of URL without https:// protocol."""
        parser = EmailParser(config_file)
        body = "See github.com/my-user/my-repo for code"
        url = parser._extract_github_url(body)
        assert url == "https://github.com/my-user/my-repo"

    def test_extract_github_url_not_found(self, config_file):
        """Test when no GitHub URL is present."""
        parser = EmailParser(config_file)
        body = "This email has no repository link"
        url = parser._extract_github_url(body)
        assert url is None

    def test_extract_github_url_case_insensitive(self, config_file):
        """Test URL extraction is case-insensitive."""
        parser = EmailParser(config_file)
        body = "Repository at GITHUB.COM/User/Repo"
        url = parser._extract_github_url(body)
        assert url is not None

    def test_github_url_variations(self, config_file, email_github_variations):
        """Test parsing different GitHub URL formats."""
        parser = EmailParser(config_file)

        for email in email_github_variations:
            result = parser.parse(email)
            assert result['repo_url'] is not None
            assert result['repo_url'].startswith('https://github.com/')
            assert not result['repo_url'].endswith('.git')


class TestSubjectValidation:
    """Tests for subject line validation."""

    def test_validate_subject_valid(self, config_file):
        """Test validation of valid subject."""
        parser = EmailParser(config_file)
        assert parser._validate_subject("Self check of homework 1")
        assert parser._validate_subject("self check of homework 42")
        assert parser._validate_subject("SELF CHECK OF HOMEWORK 100")

    def test_validate_subject_invalid(self, config_file):
        """Test validation rejects invalid subjects."""
        parser = EmailParser(config_file)
        assert not parser._validate_subject("Random subject")
        assert not parser._validate_subject("Homework submission")
        assert not parser._validate_subject("self check of homework")  # Missing number

    def test_validate_subject_case_insensitive(self, config_file):
        """Test subject validation is case-insensitive."""
        parser = EmailParser(config_file)
        subjects = [
            "self check of homework 5",
            "Self Check of Homework 5",
            "SELF CHECK OF HOMEWORK 5",
            "SeLf ChEcK oF hOmEwOrK 5"
        ]
        for subject in subjects:
            assert parser._validate_subject(subject)


class TestFieldValidation:
    """Tests for required field validation."""

    def test_check_missing_fields_all_present(self, config_file):
        """Test when all required fields are present."""
        parser = EmailParser(config_file)
        data = {
            'repo_url': 'https://github.com/user/repo',
            'sender_email': 'test@example.com'
        }
        missing = parser._check_missing_fields(data)
        assert missing == []

    def test_check_missing_fields_repo_url(self, config_file):
        """Test when repo_url is missing."""
        parser = EmailParser(config_file)
        data = {
            'repo_url': None,
            'sender_email': 'test@example.com'
        }
        missing = parser._check_missing_fields(data)
        assert 'repo_url' in missing

    def test_check_missing_fields_sender_email(self, config_file):
        """Test when sender_email is missing."""
        parser = EmailParser(config_file)
        data = {
            'repo_url': 'https://github.com/user/repo',
            'sender_email': None
        }
        missing = parser._check_missing_fields(data)
        assert 'sender_email' in missing

    def test_check_missing_fields_multiple(self, config_file):
        """Test when multiple fields are missing."""
        parser = EmailParser(config_file)
        data = {
            'repo_url': None,
            'sender_email': None
        }
        missing = parser._check_missing_fields(data)
        assert 'repo_url' in missing
        assert 'sender_email' in missing


class TestEmailParsing:
    """Tests for complete email parsing."""

    def test_parse_valid_email(self, config_file, valid_raw_email):
        """Test parsing a complete valid email."""
        parser = EmailParser(config_file)
        result = parser.parse(valid_raw_email)

        # Check all required fields are present
        assert 'email_id' in result
        assert 'message_id' in result
        assert 'email_datetime' in result
        assert 'email_subject' in result
        assert 'repo_url' in result
        assert 'sender_email' in result
        assert 'hashed_email' in result
        assert 'thread_id' in result
        assert 'status' in result
        assert 'missing_fields' in result

        # Check values
        assert result['message_id'] == valid_raw_email['message_id']
        assert result['thread_id'] == valid_raw_email['thread_id']
        assert result['sender_email'] == valid_raw_email['sender']
        assert result['email_subject'] == valid_raw_email['subject']
        assert result['email_datetime'] == valid_raw_email['datetime']
        assert result['repo_url'] is not None
        assert result['status'] == 'Ready'
        assert result['missing_fields'] == []

    def test_parse_email_without_github(self, config_file, email_without_github):
        """Test parsing email without GitHub URL."""
        parser = EmailParser(config_file)
        result = parser.parse(email_without_github)

        assert result['repo_url'] is None
        assert result['status'].startswith('Missing:')
        assert 'repo_url' in result['missing_fields']

    def test_parse_email_invalid_subject(self, config_file, email_invalid_subject):
        """Test parsing email with invalid subject (still processes)."""
        parser = EmailParser(config_file)
        result = parser.parse(email_invalid_subject)

        # Email should still be parsed, but subject won't match pattern
        assert result['email_subject'] == email_invalid_subject['subject']
        assert result['repo_url'] is not None
        assert result['status'] == 'Ready'  # Has all required fields

    def test_parse_preserves_original_fields(self, config_file, valid_raw_email):
        """Test that original fields are preserved correctly."""
        parser = EmailParser(config_file)
        result = parser.parse(valid_raw_email)

        assert result['message_id'] == valid_raw_email['message_id']
        assert result['thread_id'] == valid_raw_email['thread_id']

    def test_parse_status_ready(self, config_file, valid_raw_email):
        """Test status is 'Ready' when all fields present."""
        parser = EmailParser(config_file)
        result = parser.parse(valid_raw_email)

        assert result['status'] == 'Ready'
        assert result['missing_fields'] == []

    def test_parse_status_missing(self, config_file, email_without_github):
        """Test status indicates missing fields."""
        parser = EmailParser(config_file)
        result = parser.parse(email_without_github)

        assert 'Missing:' in result['status']
        assert 'repo_url' in result['status']
        assert len(result['missing_fields']) > 0


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_parse_empty_body(self, config_file):
        """Test parsing email with empty body."""
        parser = EmailParser(config_file)
        email = {
            'message_id': 'msg_empty',
            'thread_id': 'thread_empty',
            'sender': 'test@example.com',
            'subject': 'Self check of homework 1',
            'body': '',
            'datetime': '2026-01-11T10:00:00Z'
        }
        result = parser.parse(email)

        assert result['repo_url'] is None
        assert 'repo_url' in result['missing_fields']

    def test_parse_special_characters_in_email(self, config_file):
        """Test parsing with special characters in sender."""
        parser = EmailParser(config_file)
        email = {
            'message_id': 'msg_special',
            'thread_id': 'thread_special',
            'sender': 'test+tag@example.com',
            'subject': 'Self check of homework 5',
            'body': 'Repo: https://github.com/user/repo',
            'datetime': '2026-01-11T10:00:00Z'
        }
        result = parser.parse(email)

        assert result['sender_email'] == 'test+tag@example.com'
        assert len(result['hashed_email']) == 64  # SHA-256 hex length

    def test_parse_multiple_github_urls(self, config_file):
        """Test parsing email with multiple GitHub URLs (takes first)."""
        parser = EmailParser(config_file)
        email = {
            'message_id': 'msg_multi',
            'thread_id': 'thread_multi',
            'sender': 'test@example.com',
            'subject': 'Self check of homework 3',
            'body': 'First: https://github.com/user/repo1\nSecond: https://github.com/user/repo2',
            'datetime': '2026-01-11T10:00:00Z'
        }
        result = parser.parse(email)

        # Should extract the first URL found
        assert result['repo_url'] is not None
        assert 'user/repo1' in result['repo_url']

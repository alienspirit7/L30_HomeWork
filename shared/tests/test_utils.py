"""
Tests for Shared Utilities
"""

import pytest
from shared.utils.hash_utils import sha256_hash, generate_id
from shared.utils.validators import validate_email, validate_github_url, extract_repo_name


class TestHashUtils:
    """Tests for hash utilities."""
    
    def test_sha256_hash_returns_string(self):
        """Test sha256_hash returns a string."""
        result = sha256_hash("test")
        assert isinstance(result, str)
    
    def test_sha256_hash_consistent(self):
        """Test sha256_hash returns same hash for same input."""
        hash1 = sha256_hash("test@example.com")
        hash2 = sha256_hash("test@example.com")
        assert hash1 == hash2
    
    def test_sha256_hash_different_inputs(self):
        """Test sha256_hash returns different hashes for different inputs."""
        hash1 = sha256_hash("test1@example.com")
        hash2 = sha256_hash("test2@example.com")
        assert hash1 != hash2
    
    def test_sha256_hash_length(self):
        """Test sha256_hash returns 64 character hex string."""
        result = sha256_hash("test")
        assert len(result) == 64
    
    def test_generate_id_single_component(self):
        """Test generate_id with single component."""
        result = generate_id("user@example.com")
        assert isinstance(result, str)
        assert len(result) == 64
    
    def test_generate_id_multiple_components(self):
        """Test generate_id with multiple components."""
        result = generate_id("user@example.com", "2024-01-15", "subject")
        assert isinstance(result, str)
        assert len(result) == 64
    
    def test_generate_id_consistent(self):
        """Test generate_id returns same ID for same components."""
        id1 = generate_id("a", "b", "c")
        id2 = generate_id("a", "b", "c")
        assert id1 == id2
    
    def test_generate_id_order_matters(self):
        """Test generate_id order of components matters."""
        id1 = generate_id("a", "b")
        id2 = generate_id("b", "a")
        assert id1 != id2


class TestValidators:
    """Tests for validators."""
    
    def test_validate_email_valid(self):
        """Test validate_email returns True for valid emails."""
        assert validate_email("user@example.com") == True
        assert validate_email("user.name@domain.co.uk") == True
        assert validate_email("user+tag@example.com") == True
    
    def test_validate_email_invalid(self):
        """Test validate_email returns False for invalid emails."""
        assert validate_email("invalid") == False
        assert validate_email("@example.com") == False
        assert validate_email("user@") == False
        assert validate_email("") == False
        assert validate_email(None) == False
    
    def test_validate_github_url_valid(self):
        """Test validate_github_url returns True for valid URLs."""
        assert validate_github_url("https://github.com/user/repo") == True
        assert validate_github_url("https://github.com/user/repo.git") == True
        assert validate_github_url("http://github.com/user/repo") == True
    
    def test_validate_github_url_invalid(self):
        """Test validate_github_url returns False for invalid URLs."""
        assert validate_github_url("https://gitlab.com/user/repo") == False
        assert validate_github_url("https://github.com/user") == False
        assert validate_github_url("ftp://github.com/user/repo") == False
        assert validate_github_url("") == False
        assert validate_github_url(None) == False
    
    def test_extract_repo_name_valid(self):
        """Test extract_repo_name returns correct name."""
        assert extract_repo_name("https://github.com/user/my-repo.git") == "my-repo"
        assert extract_repo_name("https://github.com/user/my-repo") == "my-repo"
    
    def test_extract_repo_name_invalid(self):
        """Test extract_repo_name returns None for invalid URL."""
        assert extract_repo_name("invalid-url") == None
        assert extract_repo_name("") == None

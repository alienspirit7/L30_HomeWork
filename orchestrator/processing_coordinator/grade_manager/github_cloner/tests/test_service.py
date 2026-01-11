"""
Unit tests for GitHub Cloner Service
"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from service import GitHubClonerService


class TestGitHubClonerService:
    """Test suite for GitHubClonerService"""

    @pytest.fixture
    def service(self, tmp_path):
        """Create a service instance with temporary config."""
        config_path = tmp_path / "test_config.yaml"
        config_content = f"""
service:
  name: github_cloner
  version: "1.0.0"

git:
  command: "git"
  clone_args: ["--depth", "1"]

defaults:
  timeout_seconds: 30
  temp_directory: "{tmp_path}/repos"
  max_workers: 5

cleanup:
  delete_after_use: true

logging:
  level: INFO
  file: "{tmp_path}/logs/test.log"
"""
        config_path.write_text(config_content)
        return GitHubClonerService(config_path=str(config_path))

    def test_service_initialization(self, service):
        """Test service initialization."""
        assert service is not None
        assert service.config['service']['name'] == 'github_cloner'
        assert service.logger is not None

    def test_validate_url_valid(self, service):
        """Test URL validation with valid URLs."""
        assert service._validate_url("https://github.com/user/repo") is True
        assert service._validate_url("https://github.com/user/repo.git") is True

    def test_validate_url_invalid(self, service):
        """Test URL validation with invalid URLs."""
        assert service._validate_url("https://gitlab.com/user/repo") is False
        assert service._validate_url("http://example.com/repo") is False
        assert service._validate_url("not-a-url") is False

    def test_normalize_url(self, service):
        """Test URL normalization."""
        assert service._normalize_url("https://github.com/user/repo") == \
               "https://github.com/user/repo.git"
        assert service._normalize_url("https://github.com/user/repo.git") == \
               "https://github.com/user/repo.git"

    def test_clone_invalid_url(self, service):
        """Test cloning with invalid URL."""
        result = service.clone_repository("https://invalid.com/repo")
        assert result['status'] == 'Failed'
        assert result['error'] is not None
        assert 'Invalid URL format' in result['error']
        assert result['clone_path'] is None

    def test_clone_nonexistent_repo(self, service):
        """Test cloning a non-existent repository."""
        result = service.clone_repository(
            "https://github.com/nonexistent-user-12345/nonexistent-repo-67890"
        )
        assert result['status'] == 'Failed'
        assert result['error'] is not None
        assert result['clone_path'] is None

    def test_clone_success(self, service, tmp_path):
        """Test successful repository clone."""
        # Use a small public repository
        result = service.clone_repository(
            repo_url="https://github.com/octocat/Hello-World",
            destination_dir=str(tmp_path / "test_clone")
        )

        # Check result
        if result['status'] == 'Success':
            assert result['clone_path'] is not None
            assert os.path.exists(result['clone_path'])
            assert result['error'] is None
            assert result['duration_seconds'] > 0

            # Cleanup
            if os.path.exists(result['clone_path']):
                shutil.rmtree(result['clone_path'])
        else:
            # Network issues or rate limiting
            pytest.skip("Clone failed, possibly due to network or rate limiting")

    def test_clone_timeout(self, service, tmp_path):
        """Test clone timeout handling."""
        # Use very short timeout
        result = service.clone_repository(
            repo_url="https://github.com/octocat/Hello-World",
            destination_dir=str(tmp_path / "test_timeout"),
            timeout_seconds=0.001  # Extremely short timeout
        )

        assert result['status'] == 'Failed'
        assert 'timeout' in result['error'].lower()

    def test_cleanup_repository(self, service, tmp_path):
        """Test repository cleanup."""
        # Create a dummy directory
        test_dir = tmp_path / "test_cleanup"
        test_dir.mkdir()
        (test_dir / "dummy.txt").write_text("test")

        # Cleanup
        assert service.cleanup_repository(str(test_dir)) is True
        assert not os.path.exists(test_dir)

    def test_cleanup_nonexistent_path(self, service):
        """Test cleanup of non-existent path."""
        result = service.cleanup_repository("/nonexistent/path/12345")
        assert result is False

    def test_process_interface(self, service, tmp_path):
        """Test the process interface method."""
        input_data = {
            'repo_url': 'https://github.com/octocat/Hello-World',
            'destination_dir': str(tmp_path / "test_process"),
            'timeout_seconds': 30
        }

        result = service.process(input_data)

        assert 'status' in result
        assert 'clone_path' in result
        assert 'error' in result
        assert 'duration_seconds' in result

        # Cleanup if successful
        if result['status'] == 'Success' and result['clone_path']:
            if os.path.exists(result['clone_path']):
                shutil.rmtree(result['clone_path'])


class TestServiceConfiguration:
    """Test configuration handling"""

    def test_default_config_when_file_missing(self, tmp_path):
        """Test that service uses default config when file is missing."""
        service = GitHubClonerService(config_path=str(tmp_path / "nonexistent.yaml"))
        assert service.config is not None
        assert service.config['service']['name'] == 'github_cloner'

    def test_custom_config_loading(self, tmp_path):
        """Test loading custom configuration."""
        config_path = tmp_path / "custom_config.yaml"
        config_content = """
service:
  name: custom_cloner
  version: "2.0.0"

git:
  command: "git"
  clone_args: ["--depth", "1"]

defaults:
  timeout_seconds: 120
  temp_directory: "./custom/path"
  max_workers: 10

cleanup:
  delete_after_use: false

logging:
  level: DEBUG
  file: "./custom_logs/app.log"
"""
        config_path.write_text(config_content)
        service = GitHubClonerService(config_path=str(config_path))

        assert service.config['service']['name'] == 'custom_cloner'
        assert service.config['service']['version'] == '2.0.0'
        assert service.config['defaults']['timeout_seconds'] == 120
        assert service.config['defaults']['max_workers'] == 10


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

"""
GitHub Cloner Service
Clones Git repositories from GitHub to local filesystem with timeout protection.
"""

import subprocess
import os
import time
import shutil
import logging
from pathlib import Path
from typing import Dict, Optional
import yaml


class GitHubClonerService:
    """Service for cloning GitHub repositories."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the GitHub cloner service.

        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self._setup_logging()
        self.logger.info(f"GitHub Cloner Service v{self.config['service']['version']} initialized")

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file.

        Args:
            config_path: Path to config file

        Returns:
            Configuration dictionary
        """
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Use default configuration
            return {
                'service': {'name': 'github_cloner', 'version': '1.0.0'},
                'git': {'command': 'git', 'clone_args': ['--depth', '1']},
                'defaults': {
                    'timeout_seconds': 60,
                    'temp_directory': './data/tmp/repos',
                    'max_workers': 5
                },
                'cleanup': {'delete_after_use': True},
                'logging': {'level': 'INFO', 'file': './logs/github_cloner.log'}
            }

    def _setup_logging(self):
        """Setup logging configuration."""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_file = log_config.get('file', './logs/github_cloner.log')

        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        # Configure logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)

        # File handler
        fh = logging.FileHandler(log_file)
        fh.setLevel(log_level)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(log_level)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def _validate_url(self, url: str) -> bool:
        """Validate GitHub URL format.

        Args:
            url: Repository URL

        Returns:
            True if valid, False otherwise
        """
        valid_patterns = [
            'https://github.com/',
            'http://github.com/'
        ]
        return any(url.startswith(pattern) for pattern in valid_patterns)

    def _normalize_url(self, url: str) -> str:
        """Normalize GitHub URL to include .git extension.

        Args:
            url: Repository URL

        Returns:
            Normalized URL
        """
        if not url.endswith('.git'):
            return f"{url}.git"
        return url

    def clone_repository(
        self,
        repo_url: str,
        destination_dir: Optional[str] = None,
        timeout_seconds: Optional[int] = None
    ) -> Dict:
        """Clone a GitHub repository.

        Args:
            repo_url: GitHub repository URL
            destination_dir: Optional destination directory
            timeout_seconds: Optional timeout in seconds

        Returns:
            Dictionary with clone_path, status, error, and duration_seconds
        """
        start_time = time.time()

        # Validate URL
        if not self._validate_url(repo_url):
            self.logger.error(f"Invalid URL format: {repo_url}")
            return {
                'clone_path': None,
                'status': 'Failed',
                'error': f'Invalid URL format: {repo_url}. Expected https://github.com/username/repo',
                'duration_seconds': time.time() - start_time
            }

        # Normalize URL
        repo_url = self._normalize_url(repo_url)

        # Get configuration defaults
        defaults = self.config.get('defaults', {})
        timeout = timeout_seconds or defaults.get('timeout_seconds', 60)

        # Determine destination directory
        if destination_dir is None:
            temp_dir = defaults.get('temp_directory', './data/tmp/repos')
            # Extract repo name from URL
            repo_name = repo_url.rstrip('/').rstrip('.git').split('/')[-1]
            destination_dir = os.path.join(temp_dir, repo_name)

        # Ensure parent directory exists
        os.makedirs(os.path.dirname(destination_dir) or '.', exist_ok=True)

        # Build git clone command
        git_cmd = self.config.get('git', {}).get('command', 'git')
        clone_args = self.config.get('git', {}).get('clone_args', ['--depth', '1'])
        command = [git_cmd, 'clone'] + clone_args + [repo_url, destination_dir]

        self.logger.info(f"Cloning {repo_url} to {destination_dir} with timeout {timeout}s")

        try:
            # Execute git clone with timeout
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            duration = time.time() - start_time

            if result.returncode == 0:
                self.logger.info(f"Successfully cloned {repo_url} in {duration:.2f}s")
                return {
                    'clone_path': os.path.abspath(destination_dir),
                    'status': 'Success',
                    'error': None,
                    'duration_seconds': duration
                }
            else:
                # Parse error message
                error_msg = result.stderr.strip()

                # Check for specific error types
                if 'Authentication failed' in error_msg or 'access denied' in error_msg.lower():
                    error_type = 'Access denied (private repository or authentication required)'
                elif 'not found' in error_msg.lower():
                    error_type = 'Repository not found'
                elif 'network' in error_msg.lower() or 'connection' in error_msg.lower():
                    error_type = 'Network error'
                else:
                    error_type = error_msg

                self.logger.error(f"Clone failed: {error_type}")

                # Cleanup failed clone directory
                if os.path.exists(destination_dir):
                    shutil.rmtree(destination_dir)

                return {
                    'clone_path': None,
                    'status': 'Failed',
                    'error': error_type,
                    'duration_seconds': duration
                }

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            self.logger.error(f"Clone timeout after {timeout}s")

            # Cleanup on timeout
            if os.path.exists(destination_dir):
                shutil.rmtree(destination_dir)

            return {
                'clone_path': None,
                'status': 'Failed',
                'error': f'Clone operation timed out after {timeout} seconds',
                'duration_seconds': duration
            }

        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Unexpected error during clone: {str(e)}")

            # Cleanup on error
            if os.path.exists(destination_dir):
                shutil.rmtree(destination_dir)

            return {
                'clone_path': None,
                'status': 'Failed',
                'error': f'Unexpected error: {str(e)}',
                'duration_seconds': duration
            }

    def cleanup_repository(self, clone_path: str) -> bool:
        """Clean up cloned repository.

        Args:
            clone_path: Path to cloned repository

        Returns:
            True if cleanup successful, False otherwise
        """
        try:
            if os.path.exists(clone_path):
                shutil.rmtree(clone_path)
                self.logger.info(f"Cleaned up repository at {clone_path}")
                return True
            else:
                self.logger.warning(f"Repository path does not exist: {clone_path}")
                return False
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
            return False

    def process(self, input_data: Dict) -> Dict:
        """Process clone request (interface for parent service).

        Args:
            input_data: Dictionary with repo_url, destination_dir (optional),
                       timeout_seconds (optional)

        Returns:
            Dictionary with clone_path, status, error, duration_seconds
        """
        return self.clone_repository(
            repo_url=input_data['repo_url'],
            destination_dir=input_data.get('destination_dir'),
            timeout_seconds=input_data.get('timeout_seconds')
        )


def main():
    """Main entry point for standalone execution."""
    import argparse

    parser = argparse.ArgumentParser(description='GitHub Repository Cloner')
    parser.add_argument('--url', required=True, help='GitHub repository URL')
    parser.add_argument('--dest', help='Destination directory (optional)')
    parser.add_argument('--timeout', type=int, help='Timeout in seconds (optional)')
    parser.add_argument('--config', default='config.yaml', help='Config file path')

    args = parser.parse_args()

    # Create service instance
    service = GitHubClonerService(config_path=args.config)

    # Clone repository
    result = service.clone_repository(
        repo_url=args.url,
        destination_dir=args.dest,
        timeout_seconds=args.timeout
    )

    # Print result
    print("\n" + "="*60)
    print("Clone Result:")
    print("="*60)
    for key, value in result.items():
        print(f"{key}: {value}")
    print("="*60 + "\n")

    return 0 if result['status'] == 'Success' else 1


if __name__ == '__main__':
    exit(main())

"""
Email Parser Service
Extracts structured data from raw email content.
"""

import re
import hashlib
import logging
from typing import Dict, List, Optional
import yaml
from pathlib import Path


class EmailParser:
    """Parses raw email data into structured format with validation."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the email parser with configuration.

        Args:
            config_path: Path to the configuration YAML file
        """
        self.config = self._load_config(config_path)
        self._setup_logging()

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file.

        Args:
            config_path: Path to configuration file

        Returns:
            Configuration dictionary
        """
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_file, 'r') as f:
            return yaml.safe_load(f)

    def _setup_logging(self):
        """Setup logging based on configuration."""
        log_level = getattr(logging, self.config['logging']['level'])
        log_file = self.config['logging']['file']

        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Email Parser Service v{self.config['service']['version']} initialized")

    def _generate_hash(self, data: str) -> str:
        """Generate SHA-256 hash of data.

        Args:
            data: String to hash

        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def _extract_github_url(self, body: str) -> Optional[str]:
        """Extract GitHub repository URL from email body.

        Args:
            body: Email body text

        Returns:
            GitHub URL or None if not found
        """
        for pattern in self.config['patterns']['github_patterns']:
            match = re.search(pattern, body, re.IGNORECASE)
            if match:
                url = match.group(0)
                # Normalize the URL to https://github.com format
                if not url.startswith('http'):
                    url = 'https://' + url
                # Remove .git suffix if present for consistency
                url = url.rstrip('.git')
                self.logger.debug(f"Found GitHub URL: {url}")
                return url

        self.logger.warning("No GitHub URL found in email body")
        return None

    def _validate_subject(self, subject: str) -> bool:
        """Validate email subject against expected pattern.

        Args:
            subject: Email subject line

        Returns:
            True if subject matches pattern, False otherwise
        """
        pattern = self.config['patterns']['subject_pattern']
        is_valid = bool(re.search(pattern, subject, re.IGNORECASE))

        if not is_valid:
            self.logger.warning(f"Subject does not match pattern: {subject}")

        return is_valid

    def _check_missing_fields(self, parsed_data: Dict) -> List[str]:
        """Check for missing required fields.

        Args:
            parsed_data: Parsed email data

        Returns:
            List of missing field names
        """
        missing = []
        required_fields = self.config['validation']['required_fields']

        for field in required_fields:
            if field not in parsed_data or parsed_data[field] is None:
                missing.append(field)

        return missing

    def parse(self, raw_email: Dict) -> Dict:
        """Parse raw email data into structured format.

        Args:
            raw_email: Dictionary containing raw email data with keys:
                - message_id: str
                - thread_id: str
                - sender: str
                - subject: str
                - body: str
                - datetime: str

        Returns:
            Dictionary containing parsed email data:
                - email_id: SHA-256 hash
                - message_id: Original message ID
                - email_datetime: Email timestamp
                - email_subject: Email subject
                - repo_url: GitHub repository URL or None
                - sender_email: Sender email address
                - hashed_email: SHA-256 of sender
                - thread_id: Email thread ID
                - status: "Ready" or "Missing: [fields]"
                - missing_fields: List of missing fields
        """
        self.logger.info(f"Parsing email from {raw_email.get('sender', 'unknown')}")

        # Extract data
        sender = raw_email['sender']
        subject = raw_email['subject']
        body = raw_email['body']
        datetime = raw_email['datetime']
        message_id = raw_email['message_id']
        thread_id = raw_email['thread_id']

        # Generate email ID
        email_id_data = f"{sender}:{subject}:{datetime}"
        email_id = self._generate_hash(email_id_data)

        # Hash sender email
        hashed_email = self._generate_hash(sender)

        # Extract GitHub URL
        repo_url = self._extract_github_url(body)

        # Validate subject
        subject_valid = self._validate_subject(subject)
        if not subject_valid:
            self.logger.warning(f"Invalid subject format: {subject}")

        # Build parsed data
        parsed_data = {
            'email_id': email_id,
            'message_id': message_id,
            'email_datetime': datetime,
            'email_subject': subject,
            'repo_url': repo_url,
            'sender_email': sender,
            'hashed_email': hashed_email,
            'thread_id': thread_id
        }

        # Check for missing fields
        missing_fields = self._check_missing_fields(parsed_data)

        # Set status
        if missing_fields:
            status = f"Missing: {', '.join(missing_fields)}"
            self.logger.warning(f"Email {email_id[:8]}... has missing fields: {missing_fields}")
        else:
            status = "Ready"
            self.logger.info(f"Email {email_id[:8]}... successfully parsed and ready")

        parsed_data['status'] = status
        parsed_data['missing_fields'] = missing_fields

        return parsed_data


def create_parser(config_path: str = "config.yaml") -> EmailParser:
    """Factory function to create an EmailParser instance.

    Args:
        config_path: Path to configuration file

    Returns:
        EmailParser instance
    """
    return EmailParser(config_path)

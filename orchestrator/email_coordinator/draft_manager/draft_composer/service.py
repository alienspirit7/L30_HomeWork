"""
Draft Composer Service
Creates and saves email drafts in Gmail as replies to original emails.
"""

import os
import sys
import yaml
import logging
import base64
import argparse
from pathlib import Path
from email.mime.text import MIMEText
from typing import Dict, Any, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class DraftComposerService:
    """Service for creating Gmail draft replies."""

    def __init__(self, config_path: str = "./config.yaml"):
        """Initialize the Draft Composer service.

        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        self.gmail_service = None

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file.

        Args:
            config_path: Path to config file

        Returns:
            Configuration dictionary
        """
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration.

        Returns:
            Configured logger instance
        """
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_file = log_config.get('file', './logs/draft_composer.log')

        # Create logs directory if it doesn't exist
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)

        # Configure logger
        logger = logging.getLogger('draft_composer')
        logger.setLevel(log_level)

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

        logger.addHandler(fh)
        logger.addHandler(ch)

        return logger

    def _authenticate(self) -> Any:
        """Authenticate with Gmail API using OAuth2.

        Returns:
            Gmail API service instance
        """
        gmail_config = self.config['gmail']
        creds = None

        token_path = gmail_config['token_path']
        credentials_path = gmail_config['credentials_path']
        scopes = gmail_config['scopes']

        # Load existing token if available
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, scopes)

        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                self.logger.info("Refreshing expired credentials")
                creds.refresh(Request())
            else:
                self.logger.info("Starting new OAuth flow")
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, scopes
                )
                creds = flow.run_local_server(port=0)

            # Save credentials for future use
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        return build('gmail', 'v1', credentials=creds)

    def _create_draft_message(self, to: str, subject: str, body: str,
                             thread_id: str, in_reply_to: str) -> Dict[str, Any]:
        """Create a draft message structure.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content
            thread_id: Gmail thread ID for threading
            in_reply_to: Original message ID for In-Reply-To header

        Returns:
            Draft message structure
        """
        # Create MIME message
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        message['In-Reply-To'] = in_reply_to
        message['References'] = in_reply_to

        # Encode the message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        return {
            'message': {
                'raw': raw_message,
                'threadId': thread_id
            }
        }

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the draft creation request.

        Input format:
        {
            "to_email": str,
            "subject": str,
            "body": str,
            "thread_id": str,
            "in_reply_to": str
        }

        Output format:
        {
            "draft_id": str,
            "status": str,  # "Created" | "Failed"
            "error": str | None
        }

        Args:
            input_data: Draft creation request data

        Returns:
            Draft creation result
        """
        try:
            # Initialize Gmail service if not already done
            if not self.gmail_service:
                self.logger.info("Authenticating with Gmail API")
                self.gmail_service = self._authenticate()

            # Extract input parameters
            to_email = input_data['to_email']
            subject = input_data['subject']
            body = input_data['body']
            thread_id = input_data['thread_id']
            in_reply_to = input_data['in_reply_to']

            self.logger.info(f"Creating draft reply to {to_email} in thread {thread_id}")

            # Create draft message
            draft_message = self._create_draft_message(
                to=to_email,
                subject=subject,
                body=body,
                thread_id=thread_id,
                in_reply_to=in_reply_to
            )

            # Create draft via Gmail API
            draft = self.gmail_service.users().drafts().create(
                userId='me',
                body=draft_message
            ).execute()

            draft_id = draft['id']
            self.logger.info(f"Draft created successfully with ID: {draft_id}")

            return {
                "draft_id": draft_id,
                "status": "Created",
                "error": None
            }

        except HttpError as e:
            error_msg = f"Gmail API error: {str(e)}"
            self.logger.error(error_msg)
            return {
                "draft_id": None,
                "status": "Failed",
                "error": error_msg
            }
        except KeyError as e:
            error_msg = f"Missing required input field: {str(e)}"
            self.logger.error(error_msg)
            return {
                "draft_id": None,
                "status": "Failed",
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(error_msg)
            return {
                "draft_id": None,
                "status": "Failed",
                "error": error_msg
            }


def main():
    """Standalone execution entry point."""
    parser = argparse.ArgumentParser(description='Draft Composer Service')
    parser.add_argument('--to', required=True, help='Recipient email address')
    parser.add_argument('--subject', required=True, help='Email subject')
    parser.add_argument('--body', required=True, help='Email body')
    parser.add_argument('--thread-id', required=True, help='Gmail thread ID')
    parser.add_argument('--in-reply-to', required=True, help='Original message ID')
    parser.add_argument('--config', default='./config.yaml', help='Config file path')

    args = parser.parse_args()

    # Initialize service
    service = DraftComposerService(config_path=args.config)

    # Prepare input data
    input_data = {
        "to_email": args.to,
        "subject": args.subject,
        "body": args.body,
        "thread_id": args.thread_id,
        "in_reply_to": args.in_reply_to
    }

    # Process request
    result = service.process(input_data)

    # Display result
    print("\n=== Draft Composer Result ===")
    print(f"Status: {result['status']}")
    if result['draft_id']:
        print(f"Draft ID: {result['draft_id']}")
    if result['error']:
        print(f"Error: {result['error']}")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()

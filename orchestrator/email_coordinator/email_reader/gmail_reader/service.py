"""Gmail Reader Service - Reads emails from Gmail API."""

import os
import base64
import logging
from typing import Dict, List, Any
from datetime import datetime

import yaml
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GmailReaderService:
    """Service for reading emails from Gmail API."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize Gmail Reader Service.

        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        self.service = None
        self.logger.info("GmailReaderService initialized")

    def _load_config(self, config_path: str) -> Dict:
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
            Configured logger
        """
        log_config = self.config['logging']
        log_dir = os.path.dirname(log_config['file'])
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        logging.basicConfig(
            level=getattr(logging, log_config['level']),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_config['file']),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(self.config['service']['name'])

    def _authenticate(self) -> None:
        """Authenticate with Gmail API using OAuth2.

        Creates or refreshes credentials and builds the Gmail service.
        """
        creds = None
        token_path = self.config['gmail']['token_path']
        credentials_path = self.config['gmail']['credentials_path']
        scopes = self.config['gmail']['scopes']

        # Load existing token if available
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, scopes)

        # Refresh or create new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                self.logger.info("Refreshing expired credentials")
                creds.refresh(Request())
            else:
                self.logger.info("Starting OAuth flow for new credentials")
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, scopes
                )
                creds = flow.run_local_server(port=0)

            # Save credentials
            token_dir = os.path.dirname(token_path)
            if token_dir and not os.path.exists(token_dir):
                os.makedirs(token_dir)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
            self.logger.info(f"Credentials saved to {token_path}")

        # Build Gmail service
        self.service = build('gmail', 'v1', credentials=creds)
        self.logger.info("Gmail API service built successfully")

    def _decode_body(self, message: Dict) -> str:
        """Decode email body from message payload.

        Args:
            message: Gmail message object

        Returns:
            Decoded email body text
        """
        payload = message.get('payload', {})
        body = ""

        # Handle different message structures
        if 'parts' in payload:
            # Multipart message
            for part in payload['parts']:
                if part.get('mimeType') == 'text/plain':
                    data = part.get('body', {}).get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
                elif part.get('mimeType') == 'text/html' and not body:
                    data = part.get('body', {}).get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
        else:
            # Single part message
            data = payload.get('body', {}).get('data', '')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8')

        return body

    def _get_header(self, headers: List[Dict], name: str) -> str:
        """Extract header value by name.

        Args:
            headers: List of header dictionaries
            name: Header name to find

        Returns:
            Header value or empty string
        """
        for header in headers:
            if header.get('name', '').lower() == name.lower():
                return header.get('value', '')
        return ''

    def _parse_email(self, message: Dict) -> Dict[str, Any]:
        """Parse Gmail message into standardized format.

        Args:
            message: Gmail message object

        Returns:
            Parsed email dictionary
        """
        headers = message.get('payload', {}).get('headers', [])

        # Extract timestamp
        internal_date = message.get('internalDate', '0')
        timestamp = int(internal_date) / 1000.0
        datetime_str = datetime.fromtimestamp(timestamp).isoformat()

        return {
            'message_id': message.get('id', ''),
            'thread_id': message.get('threadId', ''),
            'sender': self._get_header(headers, 'From'),
            'subject': self._get_header(headers, 'Subject'),
            'body': self._decode_body(message),
            'datetime': datetime_str,
            'snippet': message.get('snippet', '')
        }

    def _mark_as_read(self, message_id: str) -> None:
        """Mark a message as read.

        Args:
            message_id: Gmail message ID
        """
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            self.logger.debug(f"Marked message {message_id} as read")
        except HttpError as e:
            self.logger.error(f"Error marking message {message_id} as read: {e}")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process request to read emails from Gmail.

        Args:
            input_data: Dictionary containing:
                - search_query: Gmail search query
                - max_results: Maximum emails to fetch
                - mark_as_read: Whether to mark as read

        Returns:
            Dictionary containing:
                - emails: List of parsed emails
                - count: Number of emails fetched
                - status: "success" or "failed"
        """
        try:
            # Authenticate if not already done
            if not self.service:
                self._authenticate()

            # Get parameters with defaults
            search_query = input_data.get(
                'search_query',
                self.config['defaults']['search_query']
            )
            max_results = input_data.get(
                'max_results',
                self.config['defaults']['max_results']
            )
            mark_as_read = input_data.get('mark_as_read', False)

            self.logger.info(f"Searching for emails: query='{search_query}', max={max_results}")

            # Search for messages
            results = self.service.users().messages().list(
                userId='me',
                q=search_query,
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])
            self.logger.info(f"Found {len(messages)} messages")

            # Fetch and parse each message
            emails = []
            for msg in messages:
                msg_id = msg['id']

                # Get full message details
                message = self.service.users().messages().get(
                    userId='me',
                    id=msg_id,
                    format='full'
                ).execute()

                # Parse email
                parsed_email = self._parse_email(message)
                emails.append(parsed_email)

                # Mark as read if requested
                if mark_as_read:
                    self._mark_as_read(msg_id)

            self.logger.info(f"Successfully processed {len(emails)} emails")

            return {
                'emails': emails,
                'count': len(emails),
                'status': 'success'
            }

        except HttpError as e:
            self.logger.error(f"Gmail API error: {e}")
            return {
                'emails': [],
                'count': 0,
                'status': 'failed'
            }
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return {
                'emails': [],
                'count': 0,
                'status': 'failed'
            }

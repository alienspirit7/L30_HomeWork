"""
Email Reader Manager
Level 2 - Task Manager

Orchestrates Gmail email fetching and email parsing into structured records.
"""

import sys
import os
import logging
from pathlib import Path
from typing import Dict, List, Any
import yaml

# Add child service paths to Python path
manager_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(manager_dir / "gmail_reader"))
sys.path.insert(0, str(manager_dir / "email_parser"))
sys.path.insert(0, str(manager_dir / "email_parser" / "src"))

try:
    from service import GmailReaderService
    from email_parser import EmailParser
except ImportError as e:
    print(f"Warning: Could not import child services: {e}")
    GmailReaderService = None
    EmailParser = None

try:
    from openpyxl import Workbook
except ImportError:
    print("Warning: openpyxl not installed. Excel output will not work.")
    Workbook = None


class EmailReaderManager:
    """
    Email Reader Manager - Level 2 Task Manager

    Manages inbound email processing by coordinating two child services:
    - Gmail Reader: Fetches raw emails from Gmail API
    - Email Parser: Extracts structured data from raw emails
    """

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the Email Reader Manager.

        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.logger = self._setup_logging()

        # Initialize child services
        self.gmail_reader = None
        self.email_parser = None
        self._initialize_child_services()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in configuration file: {e}")

    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_file = log_config.get('file', './logs/email_reader.log')
        log_format = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Create logs directory if it doesn't exist
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        # Configure logger
        logger = logging.getLogger('email_reader')
        logger.setLevel(log_level)

        # File handler
        fh = logging.FileHandler(log_file)
        fh.setLevel(log_level)
        fh.setFormatter(logging.Formatter(log_format))

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        ch.setFormatter(logging.Formatter(log_format))

        logger.addHandler(fh)
        logger.addHandler(ch)

        return logger

    def _initialize_child_services(self):
        """Initialize child services (Gmail Reader and Email Parser)."""
        children = self.config.get('children', {})
        
        # Get the directory where this manager.py is located
        manager_dir = Path(__file__).parent.absolute()

        # Initialize Gmail Reader
        gmail_reader_path = children.get('gmail_reader', './gmail_reader')
        # Resolve path relative to manager.py location
        gmail_reader_abs = (manager_dir / gmail_reader_path).resolve()
        gmail_config_path = gmail_reader_abs / 'config.yaml'

        if GmailReaderService:
            try:
                # Change working directory temporarily to gmail_reader for proper config resolution
                original_cwd = os.getcwd()
                os.chdir(gmail_reader_abs)
                self.gmail_reader = GmailReaderService(config_path=str(gmail_config_path))
                os.chdir(original_cwd)
                self.logger.info("Gmail Reader service initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Gmail Reader: {e}")
                if 'original_cwd' in locals():
                    os.chdir(original_cwd)

        # Initialize Email Parser
        email_parser_path = children.get('email_parser', './email_parser')
        email_parser_abs = (manager_dir / email_parser_path).resolve()
        parser_config_path = email_parser_abs / 'config.yaml'

        if EmailParser:
            try:
                original_cwd = os.getcwd()
                os.chdir(email_parser_abs)
                self.email_parser = EmailParser(config_path=str(parser_config_path))
                os.chdir(original_cwd)
                self.logger.info("Email Parser service initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Email Parser: {e}")
                if 'original_cwd' in locals():
                    os.chdir(original_cwd)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process emails according to input parameters.

        Args:
            input_data: Dictionary containing:
                - mode: "test" | "batch" | "full"
                - batch_size: Number of emails to fetch (optional)

        Returns:
            Dictionary containing:
                - emails: List of parsed EmailRecord objects
                - output_file: Path to generated Excel file
                - processed_count: Total emails processed
                - ready_count: Emails with status="Ready"
                - failed_count: Emails with missing fields
        """
        self.logger.info(f"Starting email processing with mode: {input_data.get('mode', 'unknown')}")

        mode = input_data.get('mode', 'test')
        batch_size = input_data.get('batch_size')

        # Determine batch size from mode if not specified
        if batch_size is None:
            modes_config = self.config.get('modes', {})
            batch_size = modes_config.get(mode, {}).get('batch_size', 5)

        # Step 1: Fetch emails from Gmail
        gmail_search_query = self.config.get('gmail_search', {}).get('query', 'is:unread')

        gmail_input = {
            'search_query': gmail_search_query,
            'max_results': batch_size,
            'mark_as_read': False
        }

        self.logger.info(f"Fetching emails with query: {gmail_search_query}, max_results: {batch_size}")

        if not self.gmail_reader:
            raise RuntimeError("Gmail Reader service not initialized")

        gmail_result = self.gmail_reader.process(gmail_input)

        if gmail_result.get('status') != 'success':
            self.logger.error("Failed to fetch emails from Gmail")
            return {
                'emails': [],
                'output_file': None,
                'processed_count': 0,
                'ready_count': 0,
                'failed_count': 0
            }

        raw_emails = gmail_result.get('emails', [])
        self.logger.info(f"Fetched {len(raw_emails)} emails from Gmail")

        # Step 2: Parse each email
        parsed_emails = []
        ready_count = 0
        failed_count = 0

        if not self.email_parser:
            raise RuntimeError("Email Parser service not initialized")

        for raw_email in raw_emails:
            try:
                parsed_email = self.email_parser.parse(raw_email)
                parsed_emails.append(parsed_email)

                if parsed_email.get('status') == 'Ready':
                    ready_count += 1
                else:
                    failed_count += 1

            except Exception as e:
                self.logger.error(f"Failed to parse email: {e}")
                failed_count += 1

        self.logger.info(f"Parsed {len(parsed_emails)} emails: {ready_count} ready, {failed_count} with issues")

        # Step 3: Write to Excel
        output_config = self.config.get('output', {})
        output_file = output_config.get('file_path', './data/output/file_1_2.xlsx')

        try:
            self._write_to_excel(parsed_emails, output_file)
            self.logger.info(f"Wrote results to {output_file}")
        except Exception as e:
            self.logger.error(f"Failed to write Excel file: {e}")
            output_file = None

        # Step 4: Return summary
        result = {
            'emails': parsed_emails,
            'output_file': output_file,
            'processed_count': len(parsed_emails),
            'ready_count': ready_count,
            'failed_count': failed_count
        }

        self.logger.info(f"Processing complete: {result['processed_count']} processed, "
                        f"{result['ready_count']} ready, {result['failed_count']} failed")

        return result

    def _write_to_excel(self, emails: List[Dict[str, Any]], output_path: str):
        """
        Write parsed emails to Excel file.

        Args:
            emails: List of parsed email dictionaries
            output_path: Path to output Excel file
        """
        if not Workbook:
            raise RuntimeError("openpyxl not installed. Cannot create Excel file.")

        # Create output directory if it doesn't exist
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create workbook and worksheet
        wb = Workbook()
        ws = wb.active
        ws.title = "Emails"

        # Write headers
        headers = [
            'email_id',
            'message_id',
            'email_datetime',
            'email_subject',
            'repo_url',
            'status',
            'hashed_email_address',
            'sender_email',
            'thread_id'
        ]
        ws.append(headers)

        # Write email data
        for email in emails:
            row = [
                email.get('email_id', ''),
                email.get('message_id', ''),
                email.get('email_datetime', ''),
                email.get('email_subject', ''),
                email.get('repo_url', ''),
                email.get('status', ''),
                email.get('hashed_email', ''),
                email.get('sender_email', ''),
                email.get('thread_id', '')
            ]
            ws.append(row)

        # Save workbook
        wb.save(output_path)


def main():
    """Main entry point for standalone execution."""
    import argparse

    parser = argparse.ArgumentParser(description='Email Reader Manager')
    parser.add_argument('--mode', choices=['test', 'batch', 'full'],
                       default='test', help='Processing mode')
    parser.add_argument('--batch-size', type=int,
                       help='Number of emails to process (overrides mode default)')
    parser.add_argument('--config', default='config.yaml',
                       help='Path to configuration file')

    args = parser.parse_args()

    # Initialize manager
    manager = EmailReaderManager(config_path=args.config)

    # Prepare input
    input_data = {
        'mode': args.mode
    }
    if args.batch_size:
        input_data['batch_size'] = args.batch_size

    # Process emails
    result = manager.process(input_data)

    # Print summary
    print("\n=== Email Reader Manager - Results ===")
    print(f"Processed: {result['processed_count']}")
    print(f"Ready: {result['ready_count']}")
    print(f"Failed: {result['failed_count']}")
    print(f"Output: {result['output_file']}")
    print("=" * 40)


if __name__ == "__main__":
    main()

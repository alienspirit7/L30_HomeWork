"""
Draft Manager - Standalone CLI Entry Point

This module provides command-line interface for running Draft Manager independently.

Usage:
    python -m draft_manager --email-file <path> --feedback-file <path>

Example:
    python -m draft_manager \
        --email-file ../email_reader/data/output/emails.xlsx \
        --feedback-file ../../processing_coordinator/feedback_manager/data/output/feedback.xlsx
"""

import argparse
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

try:
    from .manager import DraftManager
except ImportError:
    print("Error: manager.py not found. Please implement the DraftManager class.")
    print("See PRD.md for specifications.")
    sys.exit(1)


def setup_logging(
    level=logging.INFO,
    log_file=None,
    max_bytes=5*1024*1024,
    backup_count=3
):
    """
    Configure logging for CLI mode with optional file rotation.

    Args:
        level: Logging level (default: INFO)
        log_file: Path to log file (optional)
        max_bytes: Max size per log file before rotation (default: 5MB)
        backup_count: Number of backup files to keep (default: 3)
    """
    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        handlers.append(file_handler)

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Draft Manager - Personalized Email Draft Creation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process drafts from Excel files
  python -m draft_manager --email-file emails.xlsx --feedback-file feedback.xlsx

  # Use custom config
  python -m draft_manager --email-file emails.xlsx --feedback-file feedback.xlsx --config custom.yaml

  # Dry run (no actual drafts created)
  python -m draft_manager --email-file emails.xlsx --feedback-file feedback.xlsx --dry-run

  # Verbose output
  python -m draft_manager --email-file emails.xlsx --feedback-file feedback.xlsx -v
        """
    )

    parser.add_argument(
        '--email-file',
        type=str,
        required=True,
        help='Path to Excel file containing email records'
    )

    parser.add_argument(
        '--feedback-file',
        type=str,
        required=True,
        help='Path to Excel file containing feedback records'
    )

    parser.add_argument(
        '--config',
        type=str,
        default='./config.yaml',
        help='Path to configuration file (default: ./config.yaml)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate processing without creating actual drafts'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging (DEBUG level)'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    return parser.parse_args()


def load_data_files(email_file: str, feedback_file: str):
    """Load email and feedback records from Excel files."""
    import pandas as pd

    try:
        emails_df = pd.read_excel(email_file)
        feedback_df = pd.read_excel(feedback_file)

        email_records = emails_df.to_dict('records')
        feedback_records = feedback_df.to_dict('records')

        return {
            'email_records': email_records,
            'feedback_records': feedback_records
        }
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading data files: {e}")
        sys.exit(1)


def print_results(result: dict):
    """Print processing results in a formatted way."""
    print("\n" + "=" * 50)
    print("Draft Manager - Processing Results")
    print("=" * 50)

    total = result['drafts_created'] + result['drafts_failed']
    success_rate = (result['drafts_created'] / total * 100) if total > 0 else 0

    print(f"Total Drafts Created: {result['drafts_created']}")
    print(f"Total Drafts Failed: {result['drafts_failed']}")
    print(f"Success Rate: {success_rate:.1f}%")
    print("=" * 50)

    if result['draft_details']:
        print("\nDraft Details:")
        for detail in result['draft_details']:
            status_symbol = "✓" if detail['status'] == 'Created' else "✗"
            draft_info = f"draft_{detail['draft_id']}" if detail['draft_id'] else "N/A"
            error_info = f" ({detail['error']})" if detail['error'] else ""

            print(f"{status_symbol} {detail['email_id']} → {detail['status']} {draft_info}{error_info}")

    print("=" * 50 + "\n")


def main():
    """Main CLI entry point."""
    import yaml

    args = parse_arguments()

    # Determine config path (env var takes precedence)
    config_path_str = os.environ.get('DRAFT_MANAGER_CONFIG', args.config)
    config_path = Path(config_path_str)

    if not config_path.exists():
        print(f"Error: Configuration file not found: {config_path}")
        sys.exit(1)

    # Load config to get logging settings
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    logging_config = config.get('logging', {})

    # Determine log level (env var > CLI arg > config)
    if os.environ.get('DRAFT_MANAGER_LOG_LEVEL'):
        log_level_str = os.environ['DRAFT_MANAGER_LOG_LEVEL']
        log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    elif args.verbose:
        log_level = logging.DEBUG
    else:
        log_level_str = logging_config.get('level', 'INFO')
        log_level = getattr(logging, log_level_str.upper(), logging.INFO)

    # Determine log file (env var > config)
    log_file = os.environ.get('DRAFT_MANAGER_LOG_FILE', logging_config.get('file'))

    # Get rotation settings from config
    max_bytes = logging_config.get('max_bytes', 5*1024*1024)
    backup_count = logging_config.get('backup_count', 3)

    # Setup logging with rotation
    setup_logging(
        level=log_level,
        log_file=log_file,
        max_bytes=max_bytes,
        backup_count=backup_count
    )

    logger = logging.getLogger(__name__)

    # Load input data
    logger.info(f"Loading email records from: {args.email_file}")
    logger.info(f"Loading feedback records from: {args.feedback_file}")

    input_data = load_data_files(args.email_file, args.feedback_file)

    logger.info(f"Loaded {len(input_data['email_records'])} email records")
    logger.info(f"Loaded {len(input_data['feedback_records'])} feedback records")

    # Initialize Draft Manager
    logger.info(f"Initializing Draft Manager with config: {args.config}")

    try:
        manager = DraftManager(config_path=str(config_path))
    except Exception as e:
        logger.error(f"Failed to initialize Draft Manager: {e}")
        sys.exit(1)

    # Process drafts
    if args.dry_run:
        logger.info("DRY RUN MODE - No actual drafts will be created")
        # In dry run, we would simulate the process
        # For now, just log and exit
        print("\n[DRY RUN] Would process:")
        print(f"  - {len(input_data['email_records'])} emails")
        print(f"  - {len(input_data['feedback_records'])} feedback items")
        return

    logger.info("Processing email drafts...")

    try:
        result = manager.process(input_data)
        print_results(result)

        # Exit with error code if any drafts failed
        if result['drafts_failed'] > 0:
            logger.warning(f"{result['drafts_failed']} drafts failed to create")
            sys.exit(1)
        else:
            logger.info("All drafts created successfully")
            sys.exit(0)

    except Exception as e:
        logger.error(f"Error processing drafts: {e}", exc_info=args.verbose)
        sys.exit(1)


if __name__ == '__main__':
    main()

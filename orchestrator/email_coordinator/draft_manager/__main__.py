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
import sys
import logging
from pathlib import Path

try:
    from .manager import DraftManager
except ImportError:
    print("Error: manager.py not found. Please implement the DraftManager class.")
    print("See PRD.md for specifications.")
    sys.exit(1)


def setup_logging(level=logging.INFO):
    """Configure logging for CLI mode."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
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
    args = parse_arguments()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)

    logger = logging.getLogger(__name__)

    # Check if config file exists
    config_path = Path(args.config)
    if not config_path.exists():
        logger.error(f"Configuration file not found: {args.config}")
        sys.exit(1)

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

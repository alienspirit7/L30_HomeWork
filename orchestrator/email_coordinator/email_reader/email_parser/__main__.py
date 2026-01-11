"""
Email Parser Service - Standalone Execution
Run with: python -m email_parser --input sample_email.json
"""

import argparse
import json
import sys
from pathlib import Path
from src.email_parser import create_parser


def main():
    """Main entry point for standalone execution."""
    parser = argparse.ArgumentParser(
        description='Email Parser Service - Parse raw email data into structured format'
    )
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Path to input JSON file containing raw email data'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Path to output JSON file (optional, prints to stdout if not specified)'
    )

    args = parser.parse_args()

    # Check if input file exists
    input_file = Path(args.input)
    if not input_file.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Load input data
    try:
        with open(input_file, 'r') as f:
            input_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate input structure
    if 'raw_email' not in input_data:
        print("Error: Input must contain 'raw_email' key", file=sys.stderr)
        sys.exit(1)

    raw_email = input_data['raw_email']
    required_keys = ['message_id', 'thread_id', 'sender', 'subject', 'body', 'datetime']
    missing_keys = [key for key in required_keys if key not in raw_email]

    if missing_keys:
        print(f"Error: Missing required keys in raw_email: {missing_keys}", file=sys.stderr)
        sys.exit(1)

    # Create parser and process email
    try:
        email_parser = create_parser(args.config)
        result = email_parser.parse(raw_email)

        # Output result
        if args.output:
            output_file = Path(args.output)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Result written to: {args.output}")
        else:
            print(json.dumps(result, indent=2))

        # Exit with appropriate code based on status
        if result['status'] == 'Ready':
            sys.exit(0)
        else:
            print(f"\nWarning: {result['status']}", file=sys.stderr)
            sys.exit(2)

    except Exception as e:
        print(f"Error processing email: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

"""Standalone execution for Gmail Reader Service."""

import argparse
import json
from service import GmailReaderService


def main():
    """Main entry point for standalone execution."""
    parser = argparse.ArgumentParser(
        description='Gmail Reader Service - Read emails from Gmail API'
    )
    parser.add_argument(
        '--search-query',
        type=str,
        help='Gmail search query (overrides config default)'
    )
    parser.add_argument(
        '--max-results',
        type=int,
        help='Maximum number of emails to fetch (overrides config default)'
    )
    parser.add_argument(
        '--mark-as-read',
        action='store_true',
        help='Mark emails as read after fetching'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file'
    )

    args = parser.parse_args()

    # Initialize service
    service = GmailReaderService(config_path=args.config)

    # Prepare input
    input_data = {}
    if args.search_query:
        input_data['search_query'] = args.search_query
    if args.max_results:
        input_data['max_results'] = args.max_results
    if args.mark_as_read:
        input_data['mark_as_read'] = True

    # Process
    result = service.process(input_data)

    # Print results
    print("\n" + "=" * 80)
    print(f"Gmail Reader Service - Results")
    print("=" * 80)
    print(f"Status: {result['status']}")
    print(f"Count: {result['count']}")
    print("=" * 80)

    if result['emails']:
        for i, email in enumerate(result['emails'], 1):
            print(f"\n[{i}] Email:")
            print(f"  Message ID: {email['message_id']}")
            print(f"  Thread ID: {email['thread_id']}")
            print(f"  From: {email['sender']}")
            print(f"  Subject: {email['subject']}")
            print(f"  Date: {email['datetime']}")
            print(f"  Snippet: {email['snippet'][:100]}...")
            print(f"  Body Length: {len(email['body'])} characters")

    # Optionally save to file
    output_file = 'output.json'
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\n\nFull results saved to: {output_file}")


if __name__ == '__main__':
    main()

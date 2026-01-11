"""
Standalone execution module for Student Mapper service.

Usage:
    python -m src --email "student@example.com"
"""
import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from student_mapper import StudentMapper


def main():
    """Main entry point for standalone execution."""
    parser = argparse.ArgumentParser(
        description='Student Mapper Service - Map email addresses to student names'
    )
    parser.add_argument(
        '--email',
        type=str,
        required=True,
        help='Email address to look up'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='./config.yaml',
        help='Path to configuration file (default: ./config.yaml)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output result in JSON format'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show service statistics'
    )

    args = parser.parse_args()

    try:
        # Initialize the mapper
        mapper = StudentMapper(args.config)

        if args.stats:
            stats = mapper.get_stats()
            if args.json:
                print(json.dumps(stats, indent=2))
            else:
                print(f"\n{'='*50}")
                print(f"Service: {stats['service']} v{stats['version']}")
                print(f"Total Mappings: {stats['total_mappings']}")
                print(f"{'='*50}\n")

        # Perform the lookup
        result = mapper.map_email_to_name(args.email)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n{'='*50}")
            print(f"Email: {args.email}")
            print(f"Name: {result['name']}")
            print(f"Found: {'Yes' if result['found'] else 'No'}")
            print(f"{'='*50}\n")

        # Exit with appropriate code
        sys.exit(0 if result['found'] else 1)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == '__main__':
    main()

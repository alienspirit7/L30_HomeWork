"""
Main entry point for standalone execution.
Usage: python -m src --path /path/to/repository
"""
import argparse
import json
import sys
from src.service import PythonAnalyzerService


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Python Analyzer Service')
    parser.add_argument('--path', required=True, help='Path to the repository to analyze')
    parser.add_argument('--config', default='config.yaml', help='Path to config file')

    args = parser.parse_args()

    try:
        # Initialize service
        service = PythonAnalyzerService(config_path=args.config)

        # Run analysis
        results = service.analyze(args.path)

        # Print results as JSON
        print(json.dumps(results, indent=2))

        # Exit with appropriate code
        sys.exit(0 if results['status'] == 'Success' else 1)

    except Exception as e:
        print(json.dumps({
            "status": "Failed",
            "error": str(e)
        }, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

import argparse
import json
import sys
from pathlib import Path
from .service import GeminiGeneratorService


def main():
    """Standalone execution entry point."""
    parser = argparse.ArgumentParser(
        description="Gemini Generator Service - Generate AI-powered feedback"
    )
    parser.add_argument(
        "--prompt",
        type=str,
        required=True,
        help="Feedback prompt text"
    )
    parser.add_argument(
        "--style",
        type=str,
        required=True,
        help="Feedback style (e.g., constructive, encouraging, detailed)"
    )
    parser.add_argument(
        "--grade",
        type=float,
        default=0.0,
        help="Student grade (optional context)"
    )
    parser.add_argument(
        "--email-id",
        type=str,
        default="standalone",
        help="Email ID (optional context)"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to custom config.yaml file"
    )
    parser.add_argument(
        "--health",
        action="store_true",
        help="Run health check"
    )

    args = parser.parse_args()

    try:
        # Initialize service
        service = GeminiGeneratorService(config_path=args.config)

        # Run health check if requested
        if args.health:
            health_status = service.health_check()
            print(json.dumps(health_status, indent=2))
            sys.exit(0 if health_status.get("status") == "healthy" else 1)

        # Prepare input data
        input_data = {
            "prompt": args.prompt,
            "style": args.style,
            "context": {
                "grade": args.grade,
                "email_id": args.email_id
            }
        }

        print(f"\n{'='*60}")
        print("Gemini Generator Service - Standalone Execution")
        print(f"{'='*60}\n")
        print(f"Prompt: {args.prompt}")
        print(f"Style: {args.style}")
        print(f"Context: grade={args.grade}, email_id={args.email_id}\n")
        print(f"{'='*60}\n")

        # Process the request
        result = service.process(input_data)

        # Display results
        print("RESULT:")
        print(f"Status: {result['status']}")
        print(f"Tokens Used: {result['tokens_used']}")

        if result['error']:
            print(f"Error: {result['error']}")

        if result['feedback']:
            print(f"\nFeedback:\n{'-'*60}")
            print(result['feedback'])
            print(f"{'-'*60}\n")
        else:
            print("\nNo feedback generated (returned None)\n")

        # Exit with appropriate code
        sys.exit(0 if result['status'] == "Success" else 1)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
Feedback Manager Service
Level 2 - Task Manager

Orchestrates feedback generation by coordinating style_selector and gemini_generator.
Excel I/O is handled by parent coordinator.
"""

import argparse
import importlib.util
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Type

import yaml


class FeedbackManager:
    """
    Task Manager service that orchestrates feedback generation.
    Coordinates style_selector and gemini_generator services.
    """

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the Feedback Manager service.

        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self._setup_logging()
        self._initialize_child_services()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                raise FileNotFoundError(f"Config file not found: {config_path}")

            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in config file: {e}")

    def _setup_logging(self):
        """Configure logging based on config settings using module-specific logger."""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO').upper(), logging.INFO)
        log_file_config = log_config.get('file', './logs/feedback_manager.log')
        log_format = log_config.get('format',
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s')

        # Resolve log file path relative to this file's directory
        base_path = Path(__file__).parent.resolve()
        log_file = (base_path / log_file_config).resolve()

        # Create logs directory if it doesn't exist
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # Create module-specific logger (does not affect root logger)
        logger_name = self.config['manager']['name']
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(log_level)

        # Avoid adding duplicate handlers if logger already configured
        if not self.logger.handlers:
            formatter = logging.Formatter(log_format)

            # File handler
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

            # Console handler (optional)
            if log_config.get('console', True):
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(log_level)
                console_handler.setFormatter(formatter)
                self.logger.addHandler(console_handler)

        self.logger.info(
            f"Feedback Manager v{self.config['manager']['version']} initialized"
        )

    def _load_module_from_path(self, module_name: str, module_path: Path) -> Any:
        """
        Dynamically load a module from a file path using importlib.

        Args:
            module_name: Name to assign to the loaded module
            module_path: Path to the module's .py file

        Returns:
            The loaded module

        Raises:
            ImportError: If module cannot be loaded
        """
        if not module_path.exists():
            raise ImportError(f"Module file not found: {module_path}")

        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot create module spec for: {module_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    def _initialize_child_services(self):
        """Initialize child services (style_selector and gemini_generator)."""
        try:
            # Resolve paths relative to this file's directory
            base_path = Path(__file__).parent.resolve()

            style_selector_path = (base_path / self.config['children']['style_selector']).resolve()
            gemini_generator_path = (base_path / self.config['children']['gemini_generator']).resolve()

            # Load child service modules dynamically
            style_module = self._load_module_from_path(
                "style_selector_service",
                style_selector_path / "service.py"
            )
            gemini_module = self._load_module_from_path(
                "gemini_generator_service",
                gemini_generator_path / "service.py"
            )

            # Get service classes
            StyleSelector = style_module.StyleSelector
            GeminiGeneratorService = gemini_module.GeminiGeneratorService

            # Initialize services with their config files
            style_config = style_selector_path / "config.yaml"
            gemini_config = gemini_generator_path / "config.yaml"

            self.style_selector = StyleSelector(config_path=str(style_config))
            self.gemini_generator = GeminiGeneratorService(config_path=str(gemini_config))

            self.logger.info("Child services initialized successfully")
        except ImportError as e:
            self.logger.error(f"Failed to import child services: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize child services: {e}")
            raise

    def generate_feedback(self, grade_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate feedback for a single grade record.

        Args:
            grade_record: Dict with 'email_id', 'grade', etc.

        Returns:
            Dict with 'email_id', 'reply', 'status', 'error' (if any)
        """
        email_id = grade_record.get('email_id')
        grade = grade_record.get('grade')

        try:
            self.logger.debug(f"Generating feedback for {email_id}, grade: {grade}")

            # Step 1: Select style based on grade
            style_result = self.style_selector.process({'grade': grade})
            style_name = style_result['style_name']
            prompt = style_result['prompt_template']

            self.logger.debug(f"Selected style '{style_name}' for grade {grade}")

            # Step 2: Generate feedback using Gemini
            gemini_input = {
                'prompt': prompt,
                'style': style_name,
                'context': {
                    'grade': grade,
                    'email_id': email_id
                }
            }

            feedback_result = self.gemini_generator.process(gemini_input)

            # Step 3: Return result
            if feedback_result['status'] == 'Success' and feedback_result['feedback']:
                self.logger.info(f"Successfully generated feedback for {email_id}")
                return {
                    'email_id': email_id,
                    'reply': feedback_result['feedback'],
                    'status': 'Ready',
                    'error': None
                }
            else:
                # API failed
                error_msg = feedback_result.get('error', 'Unknown error')
                self.logger.warning(f"Failed to generate feedback for {email_id}: {error_msg}")
                return {
                    'email_id': email_id,
                    'reply': None,
                    'status': 'Missing: reply',
                    'error': error_msg
                }

        except Exception as e:
            self.logger.error(f"Error processing record {email_id}: {e}")
            return {
                'email_id': email_id,
                'reply': None,
                'status': 'Missing: reply',
                'error': str(e)
            }

    def process(self, grade_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Main processing method for feedback generation.
        This is the interface method called by parent coordinator.

        Args:
            grade_records: List of grade records from parent

        Returns:
            Dict with 'feedback' list, 'generated_count', 'failed_count'
        """
        self.logger.info(f"Starting feedback generation for {len(grade_records)} records")

        if not grade_records:
            self.logger.warning("No grade records to process")
            return {
                'feedback': [],
                'generated_count': 0,
                'failed_count': 0
            }

        feedback_records = []
        generated_count = 0
        failed_count = 0
        rate_limit_delay = self.config.get('rate_limiting', {}).get('delay_between_calls_seconds', 0)

        for idx, record in enumerate(grade_records, 1):
            self.logger.info(f"Processing record {idx}/{len(grade_records)}: {record.get('email_id')}")

            feedback_record = self.generate_feedback(record)
            feedback_records.append(feedback_record)

            if feedback_record['status'] == 'Ready':
                generated_count += 1
            else:
                failed_count += 1

            # Apply rate limiting between calls (except for last record)
            if idx < len(grade_records) and rate_limit_delay > 0:
                self.logger.debug(f"Rate limiting: waiting {rate_limit_delay}s")
                time.sleep(rate_limit_delay)

        result = {
            'feedback': feedback_records,
            'generated_count': generated_count,
            'failed_count': failed_count
        }

        self.logger.info(
            f"Process complete: {generated_count} generated, {failed_count} failed"
        )
        return result

    def health_check(self) -> Dict[str, str]:
        """
        Perform health check on all services.

        Returns:
            Dict with health status of all components
        """
        health = {
            'feedback_manager': 'OK',
            'style_selector': 'Unknown',
            'gemini_generator': 'Unknown'
        }

        try:
            # Test style selector
            test_result = self.style_selector.select_style(75.0)
            if test_result and 'style_name' in test_result:
                health['style_selector'] = 'OK'
            else:
                health['style_selector'] = 'Failed'
        except Exception as e:
            health['style_selector'] = f'Error: {e}'

        try:
            # Test gemini generator (just config check, not API call)
            if hasattr(self.gemini_generator, 'model'):
                health['gemini_generator'] = 'OK (API not tested)'
            else:
                health['gemini_generator'] = 'Failed'
        except Exception as e:
            health['gemini_generator'] = f'Error: {e}'

        return health


def main():
    """Main entry point for standalone execution."""
    parser = argparse.ArgumentParser(
        description='Feedback Manager Service - Orchestrate AI feedback generation'
    )
    parser.add_argument('--config', type=str, default='config.yaml',
                       help='Path to config file')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--health', action='store_true',
                       help='Run health check on all services')

    args = parser.parse_args()

    try:
        # Override log level if verbose
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        # Initialize manager
        manager = FeedbackManager(config_path=args.config)

        # Health check mode
        if args.health:
            print("\n" + "="*60)
            print("FEEDBACK MANAGER HEALTH CHECK")
            print("="*60)
            health = manager.health_check()
            for service, status in health.items():
                print(f"{service:.<30} {status}")
            print("="*60 + "\n")
            return 0

        # For standalone testing, create sample data
        print("\n" + "="*60)
        print("FEEDBACK MANAGER - Standalone Test")
        print("="*60)
        print("Note: This is a coordination service.")
        print("For full testing, use parent coordinator with real data.")
        print("\nRunning health check...")
        print("="*60)

        health = manager.health_check()
        for service, status in health.items():
            print(f"{service:.<30} {status}")
        print("="*60 + "\n")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

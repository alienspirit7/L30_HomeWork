"""
Style Selector Service
Level 3 - Leaf Service

Selects feedback style and prompt template based on student's grade.
Returns the appropriate persona and prompt for the Gemini Generator.
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

import yaml


class StyleSelector:
    """Service to select feedback style based on student grade."""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the Style Selector service.

        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.styles = self._parse_styles(self.config['styles'])
        self._setup_logging()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in config file: {e}")

    def _parse_styles(self, styles_config: List[Dict]) -> List[Dict]:
        """Parse and validate style configurations."""
        parsed = []
        for style in styles_config:
            parsed.append({
                'name': style['name'],
                'grade_range': tuple(style['grade_range']),
                'description': style['description'],
                'prompt': style['prompt'].strip()
            })
        return parsed

    def _setup_logging(self):
        """Configure logging based on config settings."""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_file = log_config.get('file', './logs/style_selector.log')

        # Create logs directory if it doesn't exist
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(self.config['service']['name'])
        self.logger.info(f"Style Selector v{self.config['service']['version']} initialized")

    def select_style(self, grade: float) -> Dict[str, str]:
        """
        Select appropriate feedback style based on grade.

        Args:
            grade: Student grade (0-100)

        Returns:
            Dictionary containing:
                - style_name: Name of the selected style
                - style_description: Description of the style
                - prompt_template: Template prompt for feedback generation

        Raises:
            ValueError: If grade is outside valid range
        """
        # Validate input
        if not isinstance(grade, (int, float)):
            raise ValueError(f"Grade must be a number, got {type(grade)}")

        if grade < 0 or grade > 100:
            raise ValueError(f"Grade must be between 0 and 100, got {grade}")

        self.logger.info(f"Selecting style for grade: {grade}")

        # Selection logic as per PRD
        if grade >= 90:
            selected_style = self._get_style_by_name("trump")
        elif grade >= 70:
            selected_style = self._get_style_by_name("hason")
        elif grade >= 55:
            selected_style = self._get_style_by_name("constructive")
        else:
            selected_style = self._get_style_by_name("amsalem")

        result = {
            "style_name": selected_style['name'],
            "style_description": selected_style['description'],
            "prompt_template": selected_style['prompt'].format(grade=grade)
        }

        self.logger.info(f"Selected style: {result['style_name']}")
        return result

    def _get_style_by_name(self, name: str) -> Dict:
        """Get style configuration by name."""
        for style in self.styles:
            if style['name'] == name:
                return style
        raise ValueError(f"Style not found: {name}")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Process input and return selected style.
        This is the main interface method for parent services.

        Args:
            input_data: Dictionary with 'grade' key

        Returns:
            Dictionary with style_name, style_description, and prompt_template
        """
        if 'grade' not in input_data:
            raise ValueError("Input must contain 'grade' field")

        return self.select_style(input_data['grade'])


def main():
    """Main entry point for standalone execution."""
    parser = argparse.ArgumentParser(description='Style Selector Service')
    parser.add_argument('--grade', type=float, required=True,
                       help='Student grade (0-100)')
    parser.add_argument('--config', type=str, default='config.yaml',
                       help='Path to config file')

    args = parser.parse_args()

    try:
        service = StyleSelector(config_path=args.config)
        result = service.select_style(args.grade)

        print("\n" + "="*60)
        print("STYLE SELECTOR RESULT")
        print("="*60)
        print(f"Grade: {args.grade}")
        print(f"Style: {result['style_name']}")
        print(f"Description: {result['style_description']}")
        print("\nPrompt Template:")
        print("-"*60)
        print(result['prompt_template'])
        print("="*60 + "\n")

        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

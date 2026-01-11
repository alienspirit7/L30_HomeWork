"""
Python Analyzer Service
Main service module that orchestrates the analysis process.
"""
import os
import yaml
import logging
from typing import Dict

from src.line_counter import LineCounter
from src.file_analyzer import FileAnalyzer
from src.grading_calculator import GradingCalculator


class PythonAnalyzerService:
    """Main service for analyzing Python repositories."""

    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self._setup_logging()
        self._initialize_components()

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            raise RuntimeError(f"Failed to load config: {e}")

    def _setup_logging(self):
        """Set up logging configuration."""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_file = log_config.get('file', './logs/python_analyzer.log')

        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _initialize_components(self):
        """Initialize service components."""
        analysis_config = self.config.get('analysis', {})
        grading_config = self.config.get('grading', {})

        # Initialize line counter
        self.line_counter = LineCounter(
            exclude_comments=grading_config.get('exclude_comments', True),
            exclude_blank_lines=grading_config.get('exclude_blank_lines', True),
            exclude_docstrings=grading_config.get('exclude_docstrings', True)
        )

        # Initialize file analyzer
        self.file_analyzer = FileAnalyzer(
            file_extensions=analysis_config.get('file_extensions', ['.py']),
            exclude_patterns=analysis_config.get('exclude_patterns', []),
            line_counter=self.line_counter
        )

        # Initialize grading calculator
        self.grading_calculator = GradingCalculator(
            line_threshold=grading_config.get('line_threshold', 150)
        )

    def analyze(self, repository_path: str) -> Dict:
        """
        Analyze a Python repository and calculate grade.

        Args:
            repository_path: Path to the repository

        Returns:
            Analysis results dictionary
        """
        try:
            self.logger.info(f"Starting analysis of repository: {repository_path}")

            # Analyze files
            file_details = self.file_analyzer.analyze_repository(repository_path)
            self.logger.info(f"Found {len(file_details)} Python files")

            # Calculate grade
            results = self.grading_calculator.calculate_grade(file_details)
            self.logger.info(f"Analysis complete. Grade: {results['grade']}")

            return results

        except Exception as e:
            self.logger.error(f"Analysis failed: {e}", exc_info=True)
            return {
                "total_files": 0,
                "total_lines": 0,
                "lines_above_150": 0,
                "grade": 0.0,
                "file_details": [],
                "status": "Failed",
                "error": str(e)
            }

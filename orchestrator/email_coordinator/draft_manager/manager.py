"""
Draft Manager - Core Implementation

Level 2 task manager that orchestrates personalized email draft creation.

This module:
1. Maps student email addresses to names (via Student Mapper)
2. Composes personalized email drafts (via Draft Composer)
3. Returns draft creation results to parent Email Coordinator
"""

import logging
import os
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError
)

# Setup logging
logger = logging.getLogger(__name__)


# Custom Exception Classes
class DraftManagerError(Exception):
    """Base exception for Draft Manager."""
    pass


class ValidationError(DraftManagerError):
    """Input validation failed."""
    pass


class RetryExhaustedError(DraftManagerError):
    """All retry attempts failed."""
    pass


# Required fields for validation
REQUIRED_EMAIL_FIELDS = ['email_id', 'sender_email']
REQUIRED_FEEDBACK_FIELDS = ['email_id', 'feedback', 'status']


class DraftManager:
    """
    Draft Manager - Level 2 Task Manager

    Orchestrates email draft creation by coordinating two child services:
    - Student Mapper: Maps email addresses to student names
    - Draft Composer: Creates Gmail drafts via API
    """

    def __init__(self, config_path: str = "./config.yaml"):
        """
        Initialize Draft Manager.

        Args:
            config_path: Path to configuration YAML file

        Raises:
            FileNotFoundError: If config file not found
            ValueError: If config is invalid
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()

        # Initialize child services
        self._init_child_services()

        logger.info(f"Draft Manager v{self.config['manager']['version']} initialized")

    def _load_config(self) -> dict:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Apply environment variable overrides
        config = self._apply_env_overrides(config)

        logger.info(f"Configuration loaded from {self.config_path}")
        return config

    def _apply_env_overrides(self, config: dict) -> dict:
        """Apply environment variable overrides to configuration."""
        # Override logging level
        if os.environ.get('DRAFT_MANAGER_LOG_LEVEL'):
            config.setdefault('logging', {})
            config['logging']['level'] = os.environ['DRAFT_MANAGER_LOG_LEVEL']
            logger.debug(f"Log level overridden by env var: {config['logging']['level']}")

        # Override log file path
        if os.environ.get('DRAFT_MANAGER_LOG_FILE'):
            config.setdefault('logging', {})
            config['logging']['file'] = os.environ['DRAFT_MANAGER_LOG_FILE']
            logger.debug(f"Log file overridden by env var: {config['logging']['file']}")

        # Override child service paths
        if os.environ.get('DRAFT_MANAGER_CHILDREN_COMPOSER'):
            config.setdefault('children', {})
            config['children']['draft_composer'] = os.environ['DRAFT_MANAGER_CHILDREN_COMPOSER']
            logger.debug(f"Draft composer path overridden by env var")

        if os.environ.get('DRAFT_MANAGER_CHILDREN_MAPPER'):
            config.setdefault('children', {})
            config['children']['student_mapper'] = os.environ['DRAFT_MANAGER_CHILDREN_MAPPER']
            logger.debug(f"Student mapper path overridden by env var")

        return config

    def _validate_input_data(self, input_data: Dict[str, Any]) -> None:
        """
        Validate input data structure and required fields.

        Args:
            input_data: Dictionary containing email_records and feedback_records

        Raises:
            ValidationError: If required fields are missing
        """
        errors = []

        # Check top-level keys
        if 'email_records' not in input_data:
            errors.append("Missing required key: 'email_records'")
        if 'feedback_records' not in input_data:
            errors.append("Missing required key: 'feedback_records'")

        if errors:
            raise ValidationError(f"Input validation failed: {'; '.join(errors)}")

        # Validate each email record has required fields
        email_records = input_data.get('email_records', [])
        for idx, record in enumerate(email_records):
            missing_fields = [f for f in REQUIRED_EMAIL_FIELDS if f not in record]
            if missing_fields:
                errors.append(
                    f"Email record {idx}: missing required fields {missing_fields}"
                )

        # Validate each feedback record has required fields
        feedback_records = input_data.get('feedback_records', [])
        for idx, record in enumerate(feedback_records):
            missing_fields = [f for f in REQUIRED_FEEDBACK_FIELDS if f not in record]
            if missing_fields:
                errors.append(
                    f"Feedback record {idx}: missing required fields {missing_fields}"
                )

        if errors:
            raise ValidationError(f"Input validation failed: {'; '.join(errors)}")

    def _init_child_services(self):
        """Initialize child services (Student Mapper and Draft Composer)."""
        # Get the directory where this manager.py is located
        manager_dir = Path(__file__).parent.absolute()
        
        # Import child services
        try:
            # Student Mapper
            student_mapper_rel = self.config['children']['student_mapper']
            student_mapper_path = (manager_dir / student_mapper_rel).resolve()
            sys.path.insert(0, str(student_mapper_path))
            
            # Change to student_mapper directory for proper imports
            original_cwd = os.getcwd()
            os.chdir(student_mapper_path)
            from src.student_mapper import StudentMapper

            self.student_mapper = StudentMapper(
                str(student_mapper_path / "config.yaml")
            )
            os.chdir(original_cwd)
            logger.info("Student Mapper service initialized")

        except ImportError as e:
            logger.error(f"Failed to import Student Mapper: {e}")
            if 'original_cwd' in locals():
                os.chdir(original_cwd)
            raise

        try:
            # Draft Composer - use importlib to avoid path conflicts
            import importlib.util
            
            draft_composer_rel = self.config['children']['draft_composer']
            draft_composer_path = (manager_dir / draft_composer_rel).resolve()
            service_file = draft_composer_path / "service.py"
            
            if not service_file.exists():
                raise ImportError(f"service.py not found at {service_file}")
            
            # Load the module explicitly from its file path
            spec = importlib.util.spec_from_file_location("draft_composer_service", service_file)
            draft_composer_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(draft_composer_module)
            
            DraftComposerService = draft_composer_module.DraftComposerService
            
            original_cwd = os.getcwd()
            os.chdir(draft_composer_path)
            self.draft_composer = DraftComposerService(
                str(draft_composer_path / "config.yaml")
            )
            os.chdir(original_cwd)
            logger.info("Draft Composer service initialized")

        except ImportError as e:
            logger.error(f"Failed to import Draft Composer: {e}")
            if 'original_cwd' in locals():
                os.chdir(original_cwd)
            raise

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process email drafts for all ready feedback records.

        Args:
            input_data: Dictionary containing:
                - email_records: List of email record dicts
                - feedback_records: List of feedback record dicts

        Returns:
            Dictionary containing:
                - drafts_created: Number of successfully created drafts
                - drafts_failed: Number of failed draft attempts
                - draft_details: List of draft detail dicts

        Example:
            >>> manager = DraftManager()
            >>> result = manager.process({
            ...     "email_records": [...],
            ...     "feedback_records": [...]
            ... })
            >>> print(result['drafts_created'])
        """
        # Validate input data
        self._validate_input_data(input_data)

        email_records = input_data.get('email_records', [])
        feedback_records = input_data.get('feedback_records', [])

        logger.info(f"Processing {len(feedback_records)} feedback records")

        # Initialize result tracking
        drafts_created = 0
        drafts_failed = 0
        draft_details = []

        # Create email lookup dict for faster access
        email_lookup = {rec['email_id']: rec for rec in email_records}

        # Process each feedback record with status="Ready"
        for feedback in feedback_records:
            if feedback.get('status') != 'Ready':
                logger.debug(f"Skipping feedback {feedback.get('email_id')} - status not Ready")
                continue

            try:
                # Process single feedback
                result = self._process_single_feedback(feedback, email_lookup)

                # Update counters
                if result['status'] == 'Created':
                    drafts_created += 1
                else:
                    drafts_failed += 1

                draft_details.append(result)

            except Exception as e:
                logger.error(f"Error processing feedback {feedback.get('email_id')}: {e}")
                drafts_failed += 1
                draft_details.append({
                    'email_id': feedback.get('email_id'),
                    'draft_id': None,
                    'status': 'Failed',
                    'error': str(e)
                })

        logger.info(f"Processing complete: {drafts_created} created, {drafts_failed} failed")

        return {
            'drafts_created': drafts_created,
            'drafts_failed': drafts_failed,
            'draft_details': draft_details
        }

    def _process_single_feedback(
        self,
        feedback: Dict[str, Any],
        email_lookup: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process a single feedback record to create a draft.

        Args:
            feedback: Feedback record dict
            email_lookup: Dictionary mapping email_id to email record

        Returns:
            Draft detail dict with status and draft_id
        """
        email_id = feedback.get('email_id')

        # Find matching email record
        email_record = email_lookup.get(email_id)
        if not email_record:
            raise ValueError(f"No email record found for email_id: {email_id}")

        # Map email to student name
        sender_email = email_record.get('sender_email')
        student_result = self.student_mapper.map_email_to_name(sender_email)
        student_name = student_result.get('name', 'Student')

        logger.debug(f"Mapped {sender_email} → {student_name}")

        # Compose email body
        email_body = self._compose_email_body(
            name=student_name,
            feedback=feedback.get('feedback', ''),
            repo_url=email_record.get('repo_url', '')
        )

        # Create draft via Draft Composer
        draft_input = {
            'to_email': sender_email,
            'subject': f"Re: {email_record.get('subject', 'Homework Feedback')}",
            'body': email_body,
            'thread_id': email_record.get('thread_id', ''),
            'in_reply_to': email_record.get('message_id', '')
        }

        try:
            draft_result = self._call_draft_composer(draft_input)
        except RetryError as e:
            raise RetryExhaustedError(
                f"All retry attempts failed for draft creation: {e}"
            ) from e

        logger.info(f"Draft {draft_result.get('status')} for {email_id}")

        return {
            'email_id': email_id,
            'draft_id': draft_result.get('draft_id'),
            'status': draft_result.get('status'),
            'error': draft_result.get('error')
        }

    def _call_draft_composer(self, draft_input: dict) -> dict:
        """
        Call draft composer with retry logic.

        Uses exponential backoff for transient failures.

        Args:
            draft_input: Dictionary containing draft parameters

        Returns:
            Draft result dictionary

        Raises:
            RetryError: If all retry attempts fail
        """
        # Get retry config with defaults
        retry_config = self.config.get('retry', {})
        max_attempts = retry_config.get('max_attempts', 3)
        min_wait = retry_config.get('min_wait_seconds', 2)
        max_wait = retry_config.get('max_wait_seconds', 10)

        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
            retry=retry_if_exception_type((ConnectionError, TimeoutError, OSError)),
            before_sleep=lambda retry_state: logger.warning(
                f"Retry {retry_state.attempt_number}/{max_attempts} for draft composer..."
            )
        )
        def _retry_call():
            return self.draft_composer.process(draft_input)

        return _retry_call()

    def _compose_email_body(
        self,
        name: str,
        feedback: str,
        repo_url: str
    ) -> str:
        """
        Compose personalized email body using template.

        Args:
            name: Student name
            feedback: Feedback content
            repo_url: Repository URL

        Returns:
            Formatted email body string
        """
        template = self.config['email_template']

        greeting = template['greeting'].format(name=name)
        repo_line = template['repo_line'].format(repo_url=repo_url)
        signature = template['signature']

        email_body = f"{greeting}\n\n{feedback}\n\n{repo_line}\n\n{signature}"

        return email_body

    def process_single(
        self,
        email_record: Dict[str, Any],
        feedback_record: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a single email and feedback record (convenience method).

        Args:
            email_record: Single email record dict
            feedback_record: Single feedback record dict

        Returns:
            Processing result dict
        """
        input_data = {
            'email_records': [email_record],
            'feedback_records': [feedback_record]
        }

        return self.process(input_data)

    def set_template(
        self,
        greeting: Optional[str] = None,
        signature: Optional[str] = None,
        repo_line: Optional[str] = None
    ):
        """
        Override email template settings.

        Args:
            greeting: Custom greeting template (use {name} placeholder)
            signature: Custom signature
            repo_line: Custom repository line (use {repo_url} placeholder)
        """
        if greeting:
            self.config['email_template']['greeting'] = greeting
        if signature:
            self.config['email_template']['signature'] = signature
        if repo_line:
            self.config['email_template']['repo_line'] = repo_line

        logger.info("Email template updated")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get manager statistics.

        Returns:
            Dictionary with manager statistics
        """
        return {
            'manager': self.config['manager']['name'],
            'version': self.config['manager']['version'],
            'student_mappings': self.student_mapper.get_stats()['total_mappings'],
            'children': {
                'student_mapper': 'active',
                'draft_composer': 'active'
            }
        }


def main():
    """Main function for testing."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("Draft Manager - Core Module")
    print("Use `python -m draft_manager` for CLI interface")
    print("\nFor programmatic usage:")
    print("  from draft_manager import DraftManager")
    print("  manager = DraftManager()")
    print("  result = manager.process(input_data)")


if __name__ == '__main__':
    main()

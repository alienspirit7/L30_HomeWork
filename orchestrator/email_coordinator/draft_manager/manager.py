"""
Draft Manager - Core Implementation

Level 2 task manager that orchestrates personalized email draft creation.

This module:
1. Maps student email addresses to names (via Student Mapper)
2. Composes personalized email drafts (via Draft Composer)
3. Returns draft creation results to parent Email Coordinator
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys

# Setup logging
logger = logging.getLogger(__name__)


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

        logger.info(f"Configuration loaded from {self.config_path}")
        return config

    def _init_child_services(self):
        """Initialize child services (Student Mapper and Draft Composer)."""
        # Import child services
        try:
            # Student Mapper
            student_mapper_path = Path(self.config['children']['student_mapper'])
            sys.path.insert(0, str(student_mapper_path))
            from src.student_mapper import StudentMapper

            self.student_mapper = StudentMapper(
                str(student_mapper_path / "config.yaml")
            )
            logger.info("Student Mapper service initialized")

        except ImportError as e:
            logger.error(f"Failed to import Student Mapper: {e}")
            raise

        try:
            # Draft Composer
            draft_composer_path = Path(self.config['children']['draft_composer'])
            sys.path.insert(0, str(draft_composer_path))
            from service import DraftComposerService

            self.draft_composer = DraftComposerService(
                str(draft_composer_path / "config.yaml")
            )
            logger.info("Draft Composer service initialized")

        except ImportError as e:
            logger.error(f"Failed to import Draft Composer: {e}")
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

        draft_result = self.draft_composer.process(draft_input)

        logger.info(f"Draft {draft_result.get('status')} for {email_id}")

        return {
            'email_id': email_id,
            'draft_id': draft_result.get('draft_id'),
            'status': draft_result.get('status'),
            'error': draft_result.get('error')
        }

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

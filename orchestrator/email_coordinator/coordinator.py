"""
Email Coordinator
Level 1 - Domain Coordinator

Coordinates all email-related operations:
- Inbound: Reading and parsing emails (via email_reader)
- Outbound: Creating email drafts (via draft_manager)
"""

import sys
import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml

# Add parent path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import child managers
try:
    from email_reader.manager import EmailReaderManager
except ImportError:
    EmailReaderManager = None

try:
    from draft_manager.manager import DraftManager
except ImportError:
    DraftManager = None

logger = logging.getLogger(__name__)


class EmailCoordinator:
    """
    Email Coordinator - Level 1 Domain Coordinator
    
    Coordinates email operations by delegating to child managers:
    - Email Reader: Fetches and parses incoming emails
    - Draft Manager: Creates outbound email drafts
    
    Actions:
    - read_emails: Fetch and parse emails from Gmail
    - create_drafts: Create draft replies with feedback
    - full_pipeline: Complete email workflow
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the Email Coordinator.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = self._load_config(config_path)
        self._setup_logging()
        self._initialize_child_managers()
        
        self.logger.info("Email Coordinator initialized")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            'coordinator': {
                'name': 'email_coordinator',
                'version': '1.0.0'
            },
            'children': {
                'email_reader': './email_reader',
                'draft_manager': './draft_manager'
            },
            'logging': {
                'level': 'INFO',
                'file': './logs/email_coordinator.log'
            }
        }
    
    def _setup_logging(self) -> None:
        """Configure logging."""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO').upper())
        log_file = log_config.get('file', './logs/email_coordinator.log')
        
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        
        if not self.logger.handlers:
            fh = logging.FileHandler(log_file)
            fh.setLevel(log_level)
            fh.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(fh)
            
            ch = logging.StreamHandler()
            ch.setLevel(log_level)
            ch.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
            self.logger.addHandler(ch)
    
    def _initialize_child_managers(self) -> None:
        """Initialize child managers."""
        children_config = self.config.get('children', {})
        base_path = Path(self.config_path).parent
        
        # Initialize Email Reader
        if EmailReaderManager is not None:
            reader_path = base_path / children_config.get('email_reader', './email_reader')
            reader_config = reader_path / 'config.yaml'
            try:
                self.email_reader = EmailReaderManager(
                    config_path=str(reader_config) if reader_config.exists() else "config.yaml"
                )
                self.logger.info("Email Reader manager initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Email Reader: {e}")
                self.email_reader = None
        else:
            self.email_reader = None
        
        # Initialize Draft Manager
        if DraftManager is not None:
            draft_path = base_path / children_config.get('draft_manager', './draft_manager')
            draft_config = draft_path / 'config.yaml'
            try:
                self.draft_manager = DraftManager(
                    config_path=str(draft_config) if draft_config.exists() else "config.yaml"
                )
                self.logger.info("Draft Manager initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Draft Manager: {e}")
                self.draft_manager = None
        else:
            self.draft_manager = None
    
    def read_emails(self, mode: str = "test", batch_size: int = 1) -> Dict[str, Any]:
        """
        Read and parse emails from Gmail.
        
        Args:
            mode: Processing mode ("test", "batch", "full")
            batch_size: Number of emails to process
            
        Returns:
            Dictionary with emails, output_file, counts
        """
        self.logger.info(f"Reading emails - mode: {mode}, batch_size: {batch_size}")
        
        if self.email_reader is None:
            return {
                'emails': [],
                'output_file': None,
                'processed_count': 0,
                'ready_count': 0,
                'failed_count': 0,
                'status': 'failed',
                'error': 'Email Reader not available'
            }
        
        try:
            result = self.email_reader.process({
                'mode': mode,
                'batch_size': batch_size
            })
            
            result['status'] = 'success'
            return result
            
        except Exception as e:
            self.logger.error(f"Error reading emails: {e}")
            return {
                'emails': [],
                'output_file': None,
                'processed_count': 0,
                'ready_count': 0,
                'failed_count': 0,
                'status': 'failed',
                'error': str(e)
            }
    
    def create_drafts(
        self, 
        email_records: List[Dict[str, Any]], 
        feedback_records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create email drafts for feedback records.
        
        Args:
            email_records: List of email record dictionaries
            feedback_records: List of feedback record dictionaries
            
        Returns:
            Dictionary with drafts_created, drafts_failed, draft_details
        """
        self.logger.info(f"Creating drafts for {len(feedback_records)} feedback records")
        
        if self.draft_manager is None:
            return {
                'drafts_created': 0,
                'drafts_failed': len(feedback_records),
                'draft_details': [],
                'status': 'failed',
                'error': 'Draft Manager not available'
            }
        
        try:
            result = self.draft_manager.process({
                'email_records': email_records,
                'feedback_records': feedback_records
            })
            
            result['status'] = 'success'
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating drafts: {e}")
            return {
                'drafts_created': 0,
                'drafts_failed': len(feedback_records),
                'draft_details': [],
                'status': 'failed',
                'error': str(e)
            }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input based on action parameter.
        
        Args:
            input_data: Dictionary with 'action' and action-specific params
            
        Returns:
            Action-specific result dictionary
        """
        action = input_data.get('action', 'read_emails')
        
        if action == 'read_emails':
            return self.read_emails(
                mode=input_data.get('mode', 'test'),
                batch_size=input_data.get('batch_size', 1)
            )
        
        elif action == 'create_drafts':
            return self.create_drafts(
                email_records=input_data.get('email_records', []),
                feedback_records=input_data.get('feedback_records', [])
            )
        
        elif action == 'full_pipeline':
            # Read emails
            email_result = self.read_emails(
                mode=input_data.get('mode', 'test'),
                batch_size=input_data.get('batch_size', 1)
            )
            
            # If feedback is provided, create drafts
            if input_data.get('feedback_records'):
                draft_result = self.create_drafts(
                    email_records=email_result.get('emails', []),
                    feedback_records=input_data.get('feedback_records', [])
                )
                return {
                    'action': 'full_pipeline',
                    'email_result': email_result,
                    'draft_result': draft_result,
                    'status': 'success'
                }
            
            return email_result
        
        else:
            return {
                'status': 'failed',
                'error': f'Unknown action: {action}'
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Check coordinator and child manager health."""
        return {
            'coordinator': 'email_coordinator',
            'status': 'healthy',
            'children': {
                'email_reader': 'healthy' if self.email_reader else 'unavailable',
                'draft_manager': 'healthy' if self.draft_manager else 'unavailable'
            }
        }


def main():
    """Main entry point for standalone execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Email Coordinator')
    parser.add_argument('--action', choices=['read_emails', 'create_drafts', 'health'],
                       default='health', help='Action to perform')
    parser.add_argument('--mode', choices=['test', 'batch', 'full'],
                       default='test', help='Processing mode')
    parser.add_argument('--batch-size', type=int, default=1,
                       help='Number of emails to process')
    parser.add_argument('--config', default='config.yaml',
                       help='Path to config file')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Email Coordinator v1.0.0")
    print("=" * 60)
    
    coordinator = EmailCoordinator(config_path=args.config)
    
    if args.action == 'health':
        health = coordinator.health_check()
        print(f"Status: {health['status']}")
        for child, status in health.get('children', {}).items():
            icon = "✓" if status == "healthy" else "✗"
            print(f"  {icon} {child}: {status}")
    
    elif args.action == 'read_emails':
        result = coordinator.read_emails(
            mode=args.mode,
            batch_size=args.batch_size
        )
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Processed: {result.get('processed_count', 0)}")
        print(f"Ready: {result.get('ready_count', 0)}")
        if result.get('error'):
            print(f"Error: {result['error']}")
    
    print("=" * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())

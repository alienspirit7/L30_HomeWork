"""
Homework Grading System - Orchestrator
Level 0 - Root Coordinator

Main entry point for the homework grading system.
Coordinates the complete workflow:
1. Read emails → email_coordinator
2. Grade repositories → processing_coordinator
3. Generate feedback → processing_coordinator
4. Create drafts → email_coordinator
"""

import sys
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import coordinators
try:
    from email_coordinator.coordinator import EmailCoordinator
except ImportError:
    EmailCoordinator = None

try:
    from processing_coordinator.coordinator import ProcessingCoordinator
except ImportError:
    ProcessingCoordinator = None


class Orchestrator:
    """
    Orchestrator - Level 0 Root Coordinator
    
    Coordinates the complete homework grading workflow by delegating to:
    - Email Coordinator: Email reading and draft creation
    - Processing Coordinator: Repository grading and feedback generation
    
    Workflow Steps:
    1. Search Emails → email_coordinator.read_emails()
    2. Clone & Grade → processing_coordinator.grade()
    3. Generate Feedback → processing_coordinator.generate_feedback()
    4. Create Drafts → email_coordinator.create_drafts()
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the Orchestrator."""
        self.config_path = config_path
        self.config = self._load_config(config_path)
        self._setup_logging()
        self._initialize_coordinators()
        
        # State
        self.current_mode = "test"
        self.batch_size = 1
        self.email_records: List[Dict] = []
        self.grade_records: List[Dict] = []
        self.feedback_records: List[Dict] = []
        
        self.logger.info("Orchestrator initialized")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            'orchestrator': {
                'name': 'homework_grading_orchestrator',
                'version': '1.0.0'
            },
            'modes': {
                'test': {'batch_size': 1},
                'batch': {'max_batch_size': 100, 'default_batch_size': 10},
                'full': {'process_all': True}
            },
            'children': {
                'email_coordinator': './email_coordinator',
                'processing_coordinator': './processing_coordinator'
            },
            'logging': {
                'level': 'INFO',
                'file': './logs/orchestrator.log'
            }
        }
    
    def _setup_logging(self) -> None:
        """Configure logging."""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO').upper())
        log_file = log_config.get('file', './logs/orchestrator.log')
        
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger('orchestrator')
        self.logger.setLevel(log_level)
        
        if not self.logger.handlers:
            fh = logging.FileHandler(log_file)
            fh.setLevel(log_level)
            fh.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(fh)
    
    def _initialize_coordinators(self) -> None:
        """Initialize child coordinators."""
        children = self.config.get('children', {})
        base_path = Path(self.config_path).parent
        
        # Initialize Email Coordinator
        if EmailCoordinator is not None:
            email_path = base_path / children.get('email_coordinator', './email_coordinator')
            email_config = email_path / 'config.yaml'
            try:
                self.email_coordinator = EmailCoordinator(
                    config_path=str(email_config) if email_config.exists() else "config.yaml"
                )
                self.logger.info("Email Coordinator initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Email Coordinator: {e}")
                self.email_coordinator = None
        else:
            self.email_coordinator = None
        
        # Initialize Processing Coordinator
        if ProcessingCoordinator is not None:
            proc_path = base_path / children.get('processing_coordinator', './processing_coordinator')
            proc_config = proc_path / 'config.yaml'
            try:
                self.processing_coordinator = ProcessingCoordinator(
                    config_path=str(proc_config) if proc_config.exists() else "config.yaml"
                )
                self.logger.info("Processing Coordinator initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Processing Coordinator: {e}")
                self.processing_coordinator = None
        else:
            self.processing_coordinator = None
    
    def set_mode(self, mode: str, batch_size: Optional[int] = None) -> None:
        """Set processing mode."""
        self.current_mode = mode
        modes = self.config.get('modes', {})
        
        if mode == 'test':
            self.batch_size = 1
        elif mode == 'batch':
            self.batch_size = batch_size or modes.get('batch', {}).get('default_batch_size', 10)
        elif mode == 'full':
            self.batch_size = 1000  # Large number for full mode
        
        self.logger.info(f"Mode set to: {mode}, batch_size: {self.batch_size}")
    
    def step1_search_emails(self) -> Dict[str, Any]:
        """Step 1: Search and parse emails from Gmail."""
        print("\n📧 Step 1: Searching Emails...")
        self.logger.info("Starting Step 1: Search Emails")
        
        if self.email_coordinator is None:
            return {'status': 'failed', 'error': 'Email Coordinator not available'}
        
        result = self.email_coordinator.read_emails(
            mode=self.current_mode,
            batch_size=self.batch_size
        )
        
        if result.get('status') == 'success':
            self.email_records = result.get('emails', [])
            print(f"   ✓ Found {len(self.email_records)} emails")
            ready_count = sum(1 for e in self.email_records if e.get('status') == 'Ready')
            print(f"   ✓ Ready for processing: {ready_count}")
        else:
            print(f"   ✗ Error: {result.get('error', 'Unknown error')}")
        
        return result
    
    def step2_clone_and_grade(self) -> Dict[str, Any]:
        """Step 2: Clone repositories and calculate grades."""
        print("\n📊 Step 2: Cloning & Grading Repositories...")
        self.logger.info("Starting Step 2: Clone & Grade")
        
        if self.processing_coordinator is None:
            return {'status': 'failed', 'error': 'Processing Coordinator not available'}
        
        if not self.email_records:
            return {'status': 'failed', 'error': 'No email records. Run Step 1 first.'}
        
        result = self.processing_coordinator.grade(self.email_records)
        
        if result.get('status') == 'success':
            self.grade_records = result.get('grades', [])
            print(f"   ✓ Graded: {result.get('graded_count', 0)} repositories")
            print(f"   ✗ Failed: {result.get('failed_count', 0)}")
        else:
            print(f"   ✗ Error: {result.get('error', 'Unknown error')}")
        
        return result
    
    def step3_generate_feedback(self) -> Dict[str, Any]:
        """Step 3: Generate AI-powered feedback."""
        print("\n🤖 Step 3: Generating AI Feedback...")
        self.logger.info("Starting Step 3: Generate Feedback")
        
        if self.processing_coordinator is None:
            return {'status': 'failed', 'error': 'Processing Coordinator not available'}
        
        if not self.grade_records:
            return {'status': 'failed', 'error': 'No grade records. Run Step 2 first.'}
        
        result = self.processing_coordinator.generate_feedback(self.grade_records)
        
        if result.get('status') == 'success':
            self.feedback_records = result.get('feedback', [])
            print(f"   ✓ Generated: {result.get('generated_count', 0)} feedback messages")
            print(f"   ✗ Failed: {result.get('failed_count', 0)}")
        else:
            print(f"   ✗ Error: {result.get('error', 'Unknown error')}")
        
        return result
    
    def step4_create_drafts(self) -> Dict[str, Any]:
        """Step 4: Create email drafts in Gmail."""
        print("\n✉️ Step 4: Creating Email Drafts...")
        self.logger.info("Starting Step 4: Create Drafts")
        
        if self.email_coordinator is None:
            return {'status': 'failed', 'error': 'Email Coordinator not available'}
        
        if not self.feedback_records:
            return {'status': 'failed', 'error': 'No feedback records. Run Step 3 first.'}
        
        result = self.email_coordinator.create_drafts(
            email_records=self.email_records,
            feedback_records=self.feedback_records
        )
        
        if result.get('status') == 'success':
            print(f"   ✓ Created: {result.get('drafts_created', 0)} drafts")
            print(f"   ✗ Failed: {result.get('drafts_failed', 0)}")
        else:
            print(f"   ✗ Error: {result.get('error', 'Unknown error')}")
        
        return result
    
    def run_all_steps(self) -> Dict[str, Any]:
        """Run complete workflow (Steps 1-4)."""
        print("\n" + "=" * 60)
        print("🚀 Running Complete Workflow")
        print("=" * 60)
        
        results = {}
        
        # Step 1
        results['step1'] = self.step1_search_emails()
        if results['step1'].get('status') != 'success':
            return {'status': 'failed', 'stopped_at': 'step1', 'results': results}
        
        # Step 2
        results['step2'] = self.step2_clone_and_grade()
        if results['step2'].get('status') != 'success':
            return {'status': 'partial', 'stopped_at': 'step2', 'results': results}
        
        # Step 3
        results['step3'] = self.step3_generate_feedback()
        if results['step3'].get('status') != 'success':
            return {'status': 'partial', 'stopped_at': 'step3', 'results': results}
        
        # Step 4
        results['step4'] = self.step4_create_drafts()
        
        print("\n" + "=" * 60)
        print("✅ Workflow Complete!")
        print("=" * 60)
        
        return {'status': 'success', 'results': results}
    
    def reset(self) -> None:
        """Reset all cached data."""
        self.email_records = []
        self.grade_records = []
        self.feedback_records = []
        print("✓ All cached data has been reset")
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of all components."""
        return {
            'orchestrator': 'homework_grading_orchestrator',
            'status': 'healthy',
            'mode': self.current_mode,
            'batch_size': self.batch_size,
            'children': {
                'email_coordinator': 'healthy' if self.email_coordinator else 'unavailable',
                'processing_coordinator': 'healthy' if self.processing_coordinator else 'unavailable'
            }
        }


def print_header():
    """Print application header."""
    print()
    print("=" * 60)
    print("        📚 Homework Grading System v1.0.0")
    print("=" * 60)


def print_mode_menu():
    """Print mode selection menu."""
    print("\n  Mode Selection:")
    print("  ─────────────────")
    print("  1. Test Mode      (1 email)")
    print("  2. Batch Mode     (N emails)")
    print("  3. Full Mode      (all unread)")
    print("  4. Exit")
    print()


def print_main_menu():
    """Print main menu."""
    print("\n  Main Menu:")
    print("  ─────────────────")
    print("  1. Search Emails         (Step 1)")
    print("  2. Clone & Grade         (Step 2)")
    print("  3. Generate Feedback     (Step 3)")
    print("  4. Create Drafts         (Step 4)")
    print("  5. Run All Steps")
    print("  6. Reset")
    print("  7. Change Mode")
    print("  8. Health Check")
    print("  9. Exit")
    print()


def run_interactive_mode(orchestrator: Orchestrator):
    """Run interactive CLI mode."""
    print_header()
    
    # Mode selection
    while True:
        print_mode_menu()
        choice = input("  Select mode [1-4]: ").strip()
        
        if choice == '1':
            orchestrator.set_mode('test')
            print("\n  ✓ Test Mode selected (1 email)")
            break
        elif choice == '2':
            try:
                n = int(input("  Enter number of emails [1-100]: ").strip())
                n = max(1, min(100, n))
                orchestrator.set_mode('batch', n)
                print(f"\n  ✓ Batch Mode selected ({n} emails)")
            except ValueError:
                orchestrator.set_mode('batch')
                print("\n  ✓ Batch Mode selected (10 emails)")
            break
        elif choice == '3':
            orchestrator.set_mode('full')
            print("\n  ✓ Full Mode selected (all unread)")
            break
        elif choice == '4':
            print("\n  Goodbye! 👋\n")
            return
    
    # Main menu loop
    while True:
        print_main_menu()
        choice = input("  Select option [1-9]: ").strip()
        
        if choice == '1':
            orchestrator.step1_search_emails()
        elif choice == '2':
            orchestrator.step2_clone_and_grade()
        elif choice == '3':
            orchestrator.step3_generate_feedback()
        elif choice == '4':
            orchestrator.step4_create_drafts()
        elif choice == '5':
            orchestrator.run_all_steps()
        elif choice == '6':
            orchestrator.reset()
        elif choice == '7':
            # Return to mode selection
            run_interactive_mode(orchestrator)
            return
        elif choice == '8':
            health = orchestrator.health_check()
            print(f"\n  Status: {health['status']}")
            print(f"  Mode: {health['mode']} (batch_size: {health['batch_size']})")
            for child, status in health.get('children', {}).items():
                icon = "✓" if status == "healthy" else "✗"
                print(f"  {icon} {child}: {status}")
        elif choice == '9':
            print("\n  Goodbye! 👋\n")
            return
        else:
            print("\n  Invalid option. Please try again.")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Homework Grading System - Automated email processing and grading'
    )
    parser.add_argument('--mode', choices=['test', 'batch', 'full'],
                       help='Processing mode')
    parser.add_argument('--batch-size', type=int, default=10,
                       help='Number of emails for batch mode')
    parser.add_argument('--step', choices=['1', '2', '3', '4', 'all'],
                       help='Run specific step or all steps')
    parser.add_argument('--config', default='config.yaml',
                       help='Path to config file')
    parser.add_argument('--health', action='store_true',
                       help='Run health check only')
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = Orchestrator(config_path=args.config)
    
    # Health check only
    if args.health:
        health = orchestrator.health_check()
        print(f"Status: {health['status']}")
        for child, status in health.get('children', {}).items():
            print(f"  {child}: {status}")
        return 0
    
    # Non-interactive mode
    if args.mode and args.step:
        orchestrator.set_mode(args.mode, args.batch_size)
        
        if args.step == '1':
            orchestrator.step1_search_emails()
        elif args.step == '2':
            orchestrator.step2_clone_and_grade()
        elif args.step == '3':
            orchestrator.step3_generate_feedback()
        elif args.step == '4':
            orchestrator.step4_create_drafts()
        elif args.step == 'all':
            orchestrator.run_all_steps()
        
        return 0
    
    # Interactive mode
    run_interactive_mode(orchestrator)
    return 0


if __name__ == '__main__':
    sys.exit(main())

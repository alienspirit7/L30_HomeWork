"""
Email Coordinator
Level 1 - Domain Coordinator for email operations
"""

__version__ = "1.0.0"

try:
    from email_coordinator.coordinator import EmailCoordinator
    __all__ = ['EmailCoordinator']
except ImportError:
    __all__ = []

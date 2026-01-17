"""
Orchestrator
Level 0 - Root Coordinator for Homework Grading System
"""

__version__ = "1.0.0"

try:
    from orchestrator.main import Orchestrator
    __all__ = ['Orchestrator']
except ImportError:
    __all__ = []

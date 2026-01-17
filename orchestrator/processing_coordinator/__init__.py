"""
Processing Coordinator
Level 1 - Domain Coordinator for processing operations
"""

__version__ = "1.0.0"

try:
    from processing_coordinator.coordinator import ProcessingCoordinator
    __all__ = ['ProcessingCoordinator']
except ImportError:
    __all__ = []

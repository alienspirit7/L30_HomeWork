"""
Coordinator Interface

Abstract base class for Level 1 coordinators and Level 2 managers 
in the BTS architecture.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class CoordinatorInterface(ABC):
    """
    Abstract interface for coordinators and managers.
    
    Used by:
    - Level 1: email_coordinator, processing_coordinator
    - Level 2: email_reader, draft_manager, grade_manager, feedback_manager
    
    Example:
        class EmailReaderManager(CoordinatorInterface):
            def process(self, input_data):
                # Coordinate gmail_reader and email_parser
                return {"emails": [...], "status": "success"}
    """
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data by coordinating child services.
        
        Args:
            input_data: Coordinator-specific input parameters
            
        Returns:
            Dictionary containing:
            - status: "success" | "partial" | "failed"
            - processed_count: Number of items processed
            - Coordinator-specific output data
            - errors: List of error messages (if any)
        """
        pass
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check coordinator and child services health.
        
        Returns:
            Dictionary with health status of coordinator and children
        """
        return {
            "coordinator": self.__class__.__name__,
            "status": "healthy",
            "children": {}
        }
    
    def get_child_services(self) -> List[str]:
        """
        Get list of child service names.
        
        Returns:
            List of child service identifiers
        """
        return []

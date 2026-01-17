"""
Service Interface

Abstract base class for Level 3 leaf services in the BTS architecture.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class ServiceInterface(ABC):
    """
    Abstract interface for Level 3 leaf services.
    
    All leaf services (gmail_reader, email_parser, github_cloner, 
    python_analyzer, style_selector, gemini_generator, student_mapper, 
    draft_composer) should implement this interface.
    
    Example:
        class GmailReaderService(ServiceInterface):
            def execute(self, input_data):
                # Fetch emails from Gmail
                return {"emails": [...], "status": "success"}
    """
    
    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the service operation.
        
        Args:
            input_data: Service-specific input parameters
            
        Returns:
            Dictionary containing:
            - status: "success" | "partial" | "failed"
            - Service-specific output data
            - errors: List of error messages (if any)
        """
        pass
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check service health status.
        
        Returns:
            Dictionary with health status information
        """
        return {
            "service": self.__class__.__name__,
            "status": "healthy"
        }

"""
Logging Utilities

Provides consistent logging configuration across all modules.
"""

import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class LoggerConfig:
    """Configuration for module logging."""
    name: str                        # Logger name
    level: str = "INFO"              # Log level
    file_path: Optional[str] = None  # Optional file output
    format: str = field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    def get_level(self) -> int:
        """Convert string level to logging constant."""
        return getattr(logging, self.level.upper(), logging.INFO)


def get_logger(
    name: str, 
    config: Optional[LoggerConfig] = None,
    level: str = "INFO",
    file_path: Optional[str] = None
) -> logging.Logger:
    """
    Get or create a configured logger.
    
    Args:
        name: Logger name (usually module __name__)
        config: Optional LoggerConfig object
        level: Log level if config not provided
        file_path: Log file path if config not provided
        
    Returns:
        Configured logger instance
        
    Example:
        >>> logger = get_logger(__name__, level="DEBUG")
        >>> logger.info("Module initialized")
    """
    if config is None:
        config = LoggerConfig(name=name, level=level, file_path=file_path)
    
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    logger.setLevel(config.get_level())
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(config.get_level())
    console_formatter = logging.Formatter(config.format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if config.file_path:
        file_path = Path(config.file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(config.file_path)
        file_handler.setLevel(config.get_level())
        file_handler.setFormatter(console_formatter)
        logger.addHandler(file_handler)
    
    return logger


def setup_root_logger(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Configure the root logger for the application.
    
    Call this once at application startup.
    
    Args:
        level: Log level for root logger
        log_file: Optional path for log file
    """
    config = LoggerConfig(
        name="root",
        level=level,
        file_path=log_file
    )
    
    root_logger = logging.getLogger()
    root_logger.setLevel(config.get_level())
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(config.get_level())
    formatter = logging.Formatter(config.format)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_path = Path(log_file)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(config.get_level())
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

"""
Environment Variable Loader

Provides environment variable loading from .env files.
"""

import os
from pathlib import Path
from typing import Optional
import logging

try:
    from dotenv import load_dotenv as dotenv_load
except ImportError:
    dotenv_load = None

logger = logging.getLogger(__name__)


def load_env(path: Optional[str] = None, override: bool = False) -> bool:
    """
    Load environment variables from .env file.
    
    Args:
        path: Path to .env file (defaults to current directory)
        override: Whether to override existing environment variables
        
    Returns:
        True if file was loaded, False otherwise
        
    Example:
        >>> load_env(".env")
        True
        >>> os.getenv("GEMINI_API_KEY")
        'your-api-key'
    """
    if dotenv_load is None:
        logger.warning("python-dotenv not installed, skipping .env loading")
        return False
    
    if path is None:
        # Search for .env in current directory and parents
        env_path = find_env_file()
    else:
        env_path = Path(path)
    
    if env_path and env_path.exists():
        dotenv_load(env_path, override=override)
        logger.debug(f"Loaded environment from {env_path}")
        return True
    
    logger.debug(f"No .env file found at {path or 'default locations'}")
    return False


def find_env_file(start_path: Optional[Path] = None) -> Optional[Path]:
    """
    Find .env file by searching current and parent directories.
    
    Args:
        start_path: Starting directory (defaults to current working directory)
        
    Returns:
        Path to .env file or None if not found
    """
    if start_path is None:
        start_path = Path.cwd()
    
    current = start_path
    for _ in range(5):  # Limit search depth
        env_file = current / ".env"
        if env_file.exists():
            return env_file
        
        parent = current.parent
        if parent == current:
            break  # Reached root
        current = parent
    
    return None


def get_env(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """
    Get environment variable with optional default.
    
    Args:
        key: Environment variable name
        default: Default value if not set
        required: If True, raise error when not found
        
    Returns:
        Environment variable value
        
    Raises:
        ValueError: If required=True and variable not found
    """
    value = os.getenv(key, default)
    
    if required and value is None:
        raise ValueError(f"Required environment variable not set: {key}")
    
    return value

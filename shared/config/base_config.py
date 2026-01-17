"""
Base Configuration

Provides YAML configuration loading for all BTS modules.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional
import logging

try:
    import yaml
except ImportError:
    yaml = None

logger = logging.getLogger(__name__)


@dataclass
class BaseConfig:
    """
    Base configuration class for YAML config loading.
    
    Each module can extend this for module-specific settings.
    
    Example:
        config = BaseConfig("config.yaml")
        print(config.get("manager.name"))
    """
    config_path: str
    _data: Dict[str, Any] = field(default_factory=dict, repr=False)
    
    def __post_init__(self):
        """Load configuration after initialization."""
        self.load()
    
    def load(self) -> None:
        """Load configuration from YAML file."""
        if yaml is None:
            raise ImportError("pyyaml is required for configuration loading")
        
        path = Path(self.config_path)
        if not path.exists():
            logger.warning(f"Config file not found: {self.config_path}")
            self._data = {}
            return
        
        with open(path, 'r') as f:
            self._data = yaml.safe_load(f) or {}
        
        logger.debug(f"Loaded config from {self.config_path}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key: Dot-separated path (e.g., "manager.name")
            default: Default value if key not found
            
        Returns:
            Configuration value or default
            
        Example:
            >>> config.get("logging.level", "INFO")
            'DEBUG'
        """
        parts = key.split('.')
        value = self._data
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        
        return value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get entire configuration section.
        
        Args:
            section: Section name (top-level key)
            
        Returns:
            Dictionary of section configuration
        """
        return self._data.get(section, {})
    
    @property
    def data(self) -> Dict[str, Any]:
        """Get raw configuration data."""
        return self._data

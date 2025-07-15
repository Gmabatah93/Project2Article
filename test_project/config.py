"""
Configuration management for the sample project.

This module handles application configuration including:
- Environment variables
- Default settings
- Configuration validation
"""

import os
from typing import Any, Dict, Optional

class Config:
    """Configuration manager for the application."""
    
    def __init__(self):
        """Initialize configuration with defaults and environment variables."""
        self._config = {
            "app_name": "Sample Project",
            "version": "1.0.0",
            "debug": False,
            "output_dir": "output",
            "max_items": 100
        }
        
        # Override with environment variables
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        env_mappings = {
            "APP_NAME": "app_name",
            "APP_VERSION": "version", 
            "DEBUG": "debug",
            "OUTPUT_DIR": "output_dir",
            "MAX_ITEMS": "max_items"
        }
        
        for env_var, config_key in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert boolean values
                if config_key == "debug":
                    self._config[config_key] = value.lower() in ("true", "1", "yes")
                elif config_key == "max_items":
                    self._config[config_key] = int(value)
                else:
                    self._config[config_key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        self._config[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary."""
        return self._config.copy() 
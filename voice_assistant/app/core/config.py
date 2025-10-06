"""
Configuration management for the voice assistant platform.
Handles loading and parsing of config.yaml file.
"""

import yaml
import os
from typing import Dict, Any
from pathlib import Path


class Config:
    """Configuration manager for the voice assistant platform."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config_data = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(config_file, 'r') as file:
            return yaml.safe_load(file)
    
    def get_module_config(self, module_name: str) -> str:
        """Get the configured module class for a given module type."""
        if module_name not in self.config_data:
            raise KeyError(f"Module '{module_name}' not found in configuration")
        
        return self.config_data[module_name]
    
    def get_all_modules(self) -> Dict[str, str]:
        """Get all configured modules."""
        return self.config_data.copy()
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting from the configuration."""
        return self.config_data.get(key, default)
    
    def reload(self):
        """Reload configuration from file."""
        self.config_data = self._load_config()


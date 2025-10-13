"""
Dynamic module loader for the voice assistant platform.
Handles loading and initialization of modules based on configuration.
"""

import importlib
import logging
from typing import Dict, Any, Type
from app.core.config import Config


class ModuleLoader:
    """Dynamic module loader for voice assistant components."""
    
    def __init__(self, config: Config):
        self.config = config
        self.modules: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
    
    def load_module(self, module_name: str) -> Any:
        """Load and initialize a single module."""
        try:
            # Get the module class path from config
            module_path = self.config.get_module_config(module_name)
            
            # Split the path into module and class name
            module_parts = module_path.split('.')
            class_name = module_parts[-1]
            module_path = '.'.join(module_parts[:-1])
            
            # Import the module
            module = importlib.import_module(f"app.modules.{module_path}")
            
            # Get the class and instantiate it
            module_class = getattr(module, class_name)
            
            # Pass config to modules that need it (like actions)
            if module_name == 'actions':
                instance = module_class(self.config.config_data)
            else:
                instance = module_class()
            
            # Initialize the module if it has an initialize method
            if hasattr(instance, 'initialize'):
                try:
                    init_result = instance.initialize()
                    if init_result:
                        self.logger.info(f"{module_name} initialized successfully")
                    else:
                        self.logger.warning(f"{module_name} initialization failed")
                except Exception as e:
                    self.logger.error(f"Failed to initialize {module_name}: {str(e)}")
            
            self.logger.info(f"{module_name}  \t => {module_path}.{class_name}")
            return instance
            
        except Exception as e:
            self.logger.error(f"Failed to load module {module_name}: {str(e)}")
            raise
    
    def load_all_modules(self) -> Dict[str, Any]:
        """Load all configured modules."""
        self.modules = {}
        
        for module_name in self.config.get_all_modules():
            # Skip non-module configuration sections
            if module_name in ['settings']:
                continue
                
            try:
                self.modules[module_name] = self.load_module(module_name)
            except Exception as e:
                self.logger.error(f"Failed to load module {module_name}: {str(e)}")
                continue #handle
        
        return self.modules
    
    def get_module(self, module_name: str) -> Any:
        """Get a loaded module by name."""
        if module_name not in self.modules:
            raise KeyError(f"Module '{module_name}' not loaded")
        return self.modules[module_name]
    
    def reload_module(self, module_name: str) -> Any:
        """Reload a specific module."""
        self.modules[module_name] = self.load_module(module_name)
        return self.modules[module_name]
    
    def reload_all_modules(self) -> Dict[str, Any]:
        """Reload all modules."""
        self.config.reload()
        return self.load_all_modules()


def initialize_modules(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Initialize all modules based on configuration."""
    config = Config(config_path)
    loader = ModuleLoader(config)
    return loader.load_all_modules()

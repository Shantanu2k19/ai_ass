"""
Base Intent Recognition module interface.
All intent recognition implementations should inherit from this base class.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging


class BaseIntent(ABC):
    """Abstract base class for Intent Recognition modules."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.is_initialized = False
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the intent recognition engine.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def recognize_intent(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Recognize intent from text input.
        
        Args:
            text (str): Input text to analyze
            **kwargs: Additional parameters for intent recognition
            
        Returns:
            Dict[str, Any]: Result containing intent, confidence, and entities
        """
        pass
    
    @abstractmethod
    def get_supported_intents(self) -> List[str]:
        """
        Get list of supported intents.
        
        Returns:
            List[str]: List of supported intent names
        """
        pass
    
    def add_intent(self, intent_name: str, examples: List[str]) -> bool:
        """
        Add a new intent with examples.
        
        Args:
            intent_name (str): Name of the intent
            examples (List[str]): Example phrases for the intent
            
        Returns:
            bool: True if intent added successfully, False otherwise
        """
        # Default implementation - can be overridden by subclasses
        self.logger.info(f"Adding intent '{intent_name}' with {len(examples)} examples")
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the intent module.
        
        Returns:
            Dict[str, Any]: Status information
        """
        return {
            "initialized": self.is_initialized,
            "supported_intents": self.get_supported_intents()
        }


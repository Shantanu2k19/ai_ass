"""
Base Actions module interface.
All action implementations should inherit from this base class.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging


class BaseActions(ABC):
    """Abstract base class for Action modules."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        # self.is_initialized = False
    
    @abstractmethod
    def execute_action(self, intent: str, entities: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Execute an action based on intent and entities.
        
        Args:
            intent (str): The recognized intent
            entities (Dict[str, Any]): Extracted entities from the input
            **kwargs: Additional parameters for action execution
            
        Returns:
            Dict[str, Any]: Result of the action execution
        """
        pass
    

    '''
    # Not required as of now
    @abstractmethod
    def get_available_actions(self) -> List[str]:
        """
        Get list of available actions.
        
        Returns:
            List[str]: List of available action names
        """
        pass
    
    def can_handle_intent(self, intent: str) -> bool:
        """
        Check if this action module can handle a specific intent.
        
        Args:
            intent (str): The intent to check
            
        Returns:
            bool: True if the module can handle the intent, False otherwise
        """
        return intent in self.get_available_actions()
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the actions module.
        
        Returns:
            Dict[str, Any]: Status information
        """
        return {
            "initialized": self.is_initialized,
            "available_actions": self.get_available_actions()
        }
    '''

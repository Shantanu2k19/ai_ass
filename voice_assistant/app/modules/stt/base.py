"""
Base Speech-to-Text (STT) module interface.
All STT implementations should inherit from this base class.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
import logging


class BaseSTT(ABC):
    """Abstract base class for Speech-to-Text modules."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.is_initialized = False
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the STT engine.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def transcribe(self, audio_data: Union[bytes, str], **kwargs) -> Dict[str, Any]:
        """
        Transcribe audio to text.
        
        Args:
            audio_data (Union[bytes, str]): Audio data as bytes or file path
            **kwargs: Additional parameters for STT engine
            
        Returns:
            Dict[str, Any]: Result containing transcribed text and confidence
        """
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> list:
        """
        Get list of supported languages.
        
        Returns:
            list: List of supported language codes
        """
        pass
    
    def set_language(self, language: str) -> bool:
        """
        Set the language for transcription.
        
        Args:
            language (str): Language code (e.g., 'en-US', 'es-ES')
            
        Returns:
            bool: True if language set successfully, False otherwise
        """
        supported_languages = self.get_supported_languages()
        if language in supported_languages:
            self.current_language = language
            return True
        else:
            self.logger.warning(f"Language '{language}' not supported. Supported languages: {supported_languages}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the STT module.
        
        Returns:
            Dict[str, Any]: Status information
        """
        return {
            "initialized": self.is_initialized,
            "current_language": getattr(self, 'current_language', None),
            "supported_languages": self.get_supported_languages()
        }


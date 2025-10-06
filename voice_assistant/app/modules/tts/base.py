"""
Base Text-to-Speech (TTS) module interface.
All TTS implementations should inherit from this base class.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging


class BaseTTS(ABC):
    """Abstract base class for Text-to-Speech modules."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.is_initialized = False
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the TTS engine.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def speak(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Convert text to speech.
        
        Args:
            text (str): Text to convert to speech
            **kwargs: Additional parameters for TTS engine
            
        Returns:
            Dict[str, Any]: Result containing audio data or file path
        """
        pass
    
    @abstractmethod
    def get_available_voices(self) -> list:
        """
        Get list of available voices.
        
        Returns:
            list: List of available voice names or IDs
        """
        pass
    
    def set_voice(self, voice: str) -> bool:
        """
        Set the voice to use for speech synthesis.
        
        Args:
            voice (str): Voice name or ID
            
        Returns:
            bool: True if voice set successfully, False otherwise
        """
        available_voices = self.get_available_voices()
        if voice in available_voices:
            self.current_voice = voice
            return True
        else:
            self.logger.warning(f"Voice '{voice}' not available. Available voices: {available_voices}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the TTS module.
        
        Returns:
            Dict[str, Any]: Status information
        """
        return {
            "initialized": self.is_initialized,
            "current_voice": getattr(self, 'current_voice', None),
            "available_voices": self.get_available_voices()
        }


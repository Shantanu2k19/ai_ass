"""
Rasa Intent Recognition implementation.
Uses trained Rasa NLU model for intent and entity extraction.
"""

import sys
import os
from typing import Dict, Any, List
from .base import BaseIntent
from .intents import ALL_INTENTS
from rasa.core.agent import Agent
from app.constants import RASA_MODEL_PATH
class RasaIntent(BaseIntent):
    """Rasa Intent Recognition implementation."""
    
    def __init__(self, model_path: str = None):
        super().__init__()
        self.model_path = model_path or RASA_MODEL_PATH
        self.agent = None
        self.supported_intents = ALL_INTENTS
    
    def initialize(self) -> bool:
        """Initialize Rasa intent recognition engine."""
        try:
            # self.logger.info(f"Loading Rasa NLU model from {self.model_path}...")
            print(f"Python Executable: {sys.executable}")
            
            print("------------------")
            self.agent = Agent.load(self.model_path)
            self.is_initialized = True
            self.logger.info("Rasa Intent Recognition initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Rasa Intent: {str(e)}")
            return False
    
    def recognize_intent(self, text: str, **kwargs) -> Dict[str, Any]:
        """Recognize intent and entities from text using Rasa."""
        if not self.is_initialized or not self.agent:
            return {"error": "Rasa Intent not initialized", "success": False}
        
        try:
            self.logger.info(f"Rasa Intent analyzing: '{text}'")
            
            import asyncio            
            try:
                loop = asyncio.get_running_loop()
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.agent.parse_message(text))
                    result = future.result()
            except RuntimeError:
                result = asyncio.run(self.agent.parse_message(text))
            
            intent = result.get("intent", {}).get("name", "unknown")
            confidence = result.get("intent", {}).get("confidence", 0.0)
            entities = {e["entity"]: e["value"] for e in result.get("entities", [])}
    
            return {
                "success": True,
                "intent": intent,
                "confidence": confidence,
                "entities": entities
            }
        except Exception as e:
            self.logger.error(f"Rasa Intent error: {str(e)}")
            return {"error": str(e), "success": False}

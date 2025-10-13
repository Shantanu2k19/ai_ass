"""
All Actions implementation.
Handles multiple intents dynamically using method mapping.
"""

from typing import Dict, Any, List, Optional
from .base import BaseActions
from .mqtt_handler import get_mqtt_handler, MQTTHandler
from app.modules.intent.intents import ALL_INTENTS, GREET, TURN_ON_DEVICE, TURN_OFF_DEVICE, ASK_TIME, ASK_DAY, ASK_DATE, OUT_OF_SCOPE
import random

class Actions(BaseActions):
    """All implementation with dynamic intent handling."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.config = config or {}
        
        # Initialize MQTT handler (optional, won't block if fails)
        self.mqtt_handler = None
        self._init_mqtt()
        
        # Dictionary mapping intents to their handler methods
        self.intent_handlers = {
            GREET: self._handle_greet,
            TURN_ON_DEVICE: self._handle_turn_on_device,
            TURN_OFF_DEVICE: self._handle_turn_off_device,
            ASK_TIME: self._handle_ask_time,
            ASK_DAY: self._handle_ask_day,
            ASK_DATE: self._handle_ask_date,
            OUT_OF_SCOPE: self._handle_out_of_scope,
        }
    
    def _init_mqtt(self):
        """Initialize MQTT handler if enabled in config."""
        try:
            mqtt_config = self.config.get('settings', {}).get('mqtt', {})
            if mqtt_config.get('enabled', False):
                self.mqtt_handler = get_mqtt_handler(mqtt_config)
                if self.mqtt_handler.is_initialized:
                    self.logger.info("MQTT handler initialized successfully")
                else:
                    self.logger.warning("MQTT handler initialization failed, continuing without MQTT")
            else:
                self.logger.info("MQTT disabled in configuration")
        except Exception as e:
            self.logger.warning(f"Failed to initialize MQTT handler: {str(e)}")
            self.mqtt_handler = None

    def execute_action(self, intent: str, entities: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Handler for all intents using dynamic method selection."""
        
        try:
            if intent not in ALL_INTENTS:
                return {
                    "success": False,
                    "error": f"Intent '{intent}' not supported",
                }
            
            # Dynamically select the handler method
            handler = self.intent_handlers.get(intent)
            if handler:
                self.logger.info(f"Executing intent: {intent} with entities: {entities}")
                return handler(entities, **kwargs)
            else:
                return {
                    "success": False,
                    "error": f"No handler found for intent '{intent}'",
                }
                
        except Exception as e:
            self.logger.error(f"Action execution error: {str(e)}")
            return {"error": str(e), "success": False}
    
    def get_available_actions(self) -> List[str]:
        """Get list of available actions."""
        return list(self.intent_handlers.keys())
    
    def publish_mqtt_message(self, topic: str, message: str, qos: Optional[int] = None) -> Dict[str, Any]:
        """
        Utility method to publish MQTT messages.
        
        Args:
            topic (str): MQTT topic to publish to
            message (str): Message to publish
            qos (int, optional): Quality of Service level
            
        Returns:
            Dict[str, Any]: Result of the publish operation
        """
        if not self.mqtt_handler or not self.mqtt_handler.is_initialized:
            return {
                "success": False,
                "error": "MQTT handler not available",
                "message": "Cannot publish message - MQTT not initialized"
            }
        
        return self.mqtt_handler.publish_message(topic, message, qos)
    
    def get_mqtt_status(self) -> Dict[str, Any]:
        """Get MQTT handler status."""
        if self.mqtt_handler:
            return self.mqtt_handler.get_status()
        else:
            return {
                "initialized": False,
                "connected": False,
                "message": "MQTT handler not initialized"
            }
    





    # Individual intent handlers, No Action required
    def _handle_greet(self, entities: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Handle greeting intent."""
        name = entities.get("name", "there")
        greeting_responses = [
            "Hi.",
            "Hello.",
            "Hey there.",
            "Hello there.",
            "Hi, how can I help?",
            "Hey, how can I assist?",
            "Hello, how can I help?",
            "Hi, ready for your command.",
            "Hey there, what can I do for you?",
            "Hi, I am Online and ready.",
            "Hi, All Systems active. How can I help?",
        ]
        return {
            "success": True,
            "speech_op": random.choice(greeting_responses),
        }
    

    #Relay action 
    def _handle_turn_on_device(self, entities: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Handle turn on device intent."""
        device = entities.get("device", None)
        eta = entities.get("eta", None)

        if eta:
            #TODO implement
            pass

        if not device:
            return {
                "success": False,
                "message": "Device not specified"
            }        

        # Try to control device via MQTT
        if self.mqtt_handler and self.mqtt_handler.is_initialized:
            topic = f"home/myroom/{device}"
            message = "ON"
            
            mqtt_result = self.mqtt_handler.publish_message(topic, message)
            
            if mqtt_result.get("success", False):
                return {
                    "success": True,
                    "speech_op": "Turning on " + device
                }
            else:
                return { "success": False }
        else:
            return { "success": False }
    
    def _handle_turn_off_device(self, entities: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Handle turn off device intent."""
        device = entities.get("device", None)
        eta = entities.get("eta", None)

        if eta:
            #TODO implement
            pass

        if not device:
            return {
                "success": False,
                "message": "Device not specified"
            }

        # Try to control device via MQTT
        if self.mqtt_handler and self.mqtt_handler.is_initialized:
            topic = f"home/myroom/{device}"
            message = "OFF"
            
            mqtt_result = self.mqtt_handler.publish_message(topic, message)
            
            if mqtt_result.get("success", False):
                return {
                    "success": True,
                    "speech_op": f"Turning off {device}",
                }
            else:
                return { "success": False }
        else:
            return { "success": False }

    def _handle_ask_time(self, entities: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Handle ask time intent."""
        from datetime import datetime
        
        current_time = datetime.now().strftime("%I:%M %p")
        return {
            "success": True,
            "speech_op": f"The current time is {current_time}",
        }
    
    def _handle_ask_day(self, entities: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Handle ask day intent."""
        from datetime import datetime
        
        current_day = datetime.now().strftime("%A")
        return {
            "success": True,
            "speech_op": f"Today is {current_day}",
        }
    
    def _handle_ask_date(self, entities: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Handle ask date intent."""
        from datetime import datetime
        
        current_date = datetime.now().strftime("%B %d, %Y")
        return {
            "success": True,
            "speech_op": f"Today's date is {current_date}",
        }
    
    def _handle_out_of_scope(self, entities: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Handle out of scope intent."""
        return {
            "success": False,
            "message": "I'm sorry, I didn't understand that. Could you please rephrase?",
        }


"""
MQTT Handler Module
Provides optional MQTT functionality for device control.
Designed to not block project initialization if MQTT is unavailable.
"""

import paho.mqtt.client as mqtt
import logging
from typing import Dict, Any, Optional, Callable
import threading
import time
from app.core.config import Config

class MQTTHandler:
    """MQTT Handler for device control with optional initialization."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.is_initialized = False
        self.is_connected = False
        self.client = None
        self.config = config or {}
        self.connection_lock = threading.Lock()
        
        # MQTT Configuration with defaults
        self.broker_host = self.config.get('mqtt', {}).get('broker_host', 'localhost')
        self.broker_port = self.config.get('mqtt', {}).get('broker_port', 1883)
        self.username = self.config.get('mqtt', {}).get('username', None)
        self.password = self.config.get('mqtt', {}).get('password', None)
        self.keepalive = self.config.get('mqtt', {}).get('keepalive', 60)
        self.qos = self.config.get('mqtt', {}).get('qos', 0)
        
        # Try to initialize MQTT (non-blocking)
        self._try_initialize()
    
    def _try_initialize(self) -> bool:
        """Try to initialize MQTT connection without blocking."""
        try:
            self.client = mqtt.Client()
            
            # Set up callbacks
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_publish = self._on_publish
            self.client.on_log = self._on_log
            
            # Set authentication if provided
            if self.username and self.password:
                self.client.username_pw_set(self.username, self.password)
            
            self.is_initialized = True
            self.logger.info("MQTT client initialized successfully")
            return True
            
        except Exception as e:
            self.logger.warning(f"Failed to initialize MQTT client: {str(e)}")
            self.is_initialized = False
            return False
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for when the client connects to the broker."""
        if rc == 0:
            self.is_connected = True
            self.logger.info("Connected to MQTT broker successfully")
        else:
            self.is_connected = False
            self.logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects from the broker."""
        self.is_connected = False
        if rc != 0:
            self.logger.warning(f"Unexpected disconnection from MQTT broker. Return code: {rc}")
        else:
            self.logger.info("Disconnected from MQTT broker")
    
    def _on_publish(self, client, userdata, mid):
        """Callback for when a message is published."""
        self.logger.debug(f"Message published with mid: {mid}")
    
    def _on_log(self, client, userdata, level, buf):
        """Callback for MQTT logging."""
        self.logger.debug(f"MQTT Log: {buf}")
    
    def connect(self) -> bool:
        """Connect to MQTT broker."""
        if not self.is_initialized:
            self.logger.error("MQTT client not initialized")
            return False
        
        try:
            with self.connection_lock:
                if not self.is_connected:
                    self.client.connect(self.broker_host, self.broker_port, self.keepalive)
                    self.client.loop_start()  # Start the loop in a separate thread
                    
                    # Wait a bit for connection to establish
                    time.sleep(0.5)
                    
            return self.is_connected
            
        except Exception as e:
            self.logger.error(f"Failed to connect to MQTT broker: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker."""
        if self.client and self.is_connected:
            try:
                self.client.loop_stop()
                self.client.disconnect()
                self.logger.info("Disconnected from MQTT broker")
            except Exception as e:
                self.logger.error(f"Error disconnecting from MQTT broker: {str(e)}")
    
    def publish_message(self, topic: str, message: str, qos: Optional[int] = None) -> Dict[str, Any]:
        """
        Publish a message to MQTT topic.
        
        Args:
            topic (str): MQTT topic to publish to
            message (str): Message to publish
            qos (int, optional): Quality of Service level
            
        Returns:
            Dict[str, Any]: Result of the publish operation
        """
        if not self.is_initialized:
            return {
                "success": False,
                "error": "MQTT client not initialized",
                "message": "MQTT functionality not available"
            }
        
        if not self.is_connected:
            # Try to connect
            if not self.connect():
                return {
                    "success": False,
                    "error": "Failed to connect to MQTT broker",
                    "message": "Cannot publish message - MQTT not available"
                }
        
        try:
            qos_level = qos if qos is not None else self.qos
            result = self.client.publish(topic, message, qos=qos_level)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.info(f"Published message to topic '{topic}': {message}")
                return {
                    "success": True,
                    "message": f"Message published to {topic}",
                    "topic": topic,
                    "payload": message,
                    "qos": qos_level
                }
            else:
                self.logger.error(f"Failed to publish message. Error code: {result.rc}")
                return {
                    "success": False,
                    "error": f"Publish failed with error code: {result.rc}",
                    "message": "Failed to publish message"
                }
                
        except Exception as e:
            self.logger.error(f"Error publishing message: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Error occurred while publishing message"
            }
    
    def subscribe_to_topic(self, topic: str, callback: Optional[Callable] = None, qos: int = 0) -> Dict[str, Any]:
        """
        Subscribe to an MQTT topic.
        
        Args:
            topic (str): Topic to subscribe to
            callback (Callable, optional): Callback function for received messages
            qos (int): Quality of Service level
            
        Returns:
            Dict[str, Any]: Result of the subscription
        """
        if not self.is_initialized:
            return {
                "success": False,
                "error": "MQTT client not initialized"
            }
        
        if not self.is_connected:
            if not self.connect():
                return {
                    "success": False,
                    "error": "Failed to connect to MQTT broker"
                }
        
        try:
            if callback:
                self.client.message_callback_add(topic, callback)
            
            result = self.client.subscribe(topic, qos)
            
            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                self.logger.info(f"Subscribed to topic: {topic}")
                return {
                    "success": True,
                    "message": f"Subscribed to {topic}",
                    "topic": topic
                }
            else:
                self.logger.error(f"Failed to subscribe to topic. Error code: {result[0]}")
                return {
                    "success": False,
                    "error": f"Subscription failed with error code: {result[0]}"
                }
                
        except Exception as e:
            self.logger.error(f"Error subscribing to topic: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current MQTT handler status."""
        return {
            "initialized": self.is_initialized,
            "connected": self.is_connected,
            "broker_host": self.broker_host,
            "broker_port": self.broker_port,
            "username": self.username is not None,
            "qos": self.qos
        }
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.disconnect()


# Global MQTT handler instance
_mqtt_handler = None

def get_mqtt_handler(config: Optional[Dict[str, Any]] = None) -> MQTTHandler:
    """Get or create the global MQTT handler instance."""
    global _mqtt_handler
    if _mqtt_handler is None:
        _mqtt_handler = MQTTHandler(config)
    return _mqtt_handler

def initialize_mqtt(config: Optional[Dict[str, Any]] = None) -> bool:
    """Initialize MQTT handler with optional configuration."""
    global _mqtt_handler
    _mqtt_handler = MQTTHandler(config)
    return _mqtt_handler.is_initialized

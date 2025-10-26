#!/usr/bin/env python3
"""
MQTT Example Script
Demonstrates how to use the MQTT handler for device control.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.modules.actions.mqtt_handler import get_mqtt_handler, initialize_mqtt
from app.core.config import Config
import time

def main():
    """Example usage of MQTT handler."""
    print("MQTT Handler Example")
    print("=" * 50)
    
    # Load configuration
    config = Config("config.yaml")
    mqtt_config = config.config_data.get('settings', {}).get('mqtt', {})
    
    print(f"MQTT Configuration: {mqtt_config}")
    print()
    
    # Initialize MQTT handler
    print("Initializing MQTT handler...")
    mqtt_handler = get_mqtt_handler(mqtt_config)
    
    if not mqtt_handler.is_initialized:
        print("MQTT handler initialization failed!")
        print("This is expected if MQTT broker is not available.")
        print("The application will continue without MQTT functionality.")
        return
    
    print("MQTT handler initialized successfully!")
    print()
    
    # Get MQTT status
    status = mqtt_handler.get_status()
    print(f"MQTT Status: {status}")
    print()
    
    # Example 1: Publish a simple message
    print("Example 1: Publishing a simple message")
    topic = "home/living_room/light"
    message = "ON"
    
    result = mqtt_handler.publish_message(topic, message)
    print(f"Publish result: {result}")
    print()
    
    # Example 2: Publish with different QoS
    print("Example 2: Publishing with QoS 1")
    topic2 = "home/kitchen/fan"
    message2 = "OFF"
    
    result2 = mqtt_handler.publish_message(topic2, message2, qos=1)
    print(f"Publish result: {result2}")
    print()
    
    # Example 3: Try to publish when disconnected
    print("Example 3: Disconnecting and trying to publish")
    mqtt_handler.disconnect()
    
    result3 = mqtt_handler.publish_message("test/topic", "test message")
    print(f"Publish result (after disconnect): {result3}")
    print()
    
    # Example 4: Reconnect and publish
    print("Example 4: Reconnecting and publishing")
    if mqtt_handler.connect():
        result4 = mqtt_handler.publish_message("home/bedroom/light", "ON")
        print(f"Publish result (after reconnect): {result4}")
    else:
        print("Failed to reconnect to MQTT broker")
    
    print()
    print("Example completed!")

if __name__ == "__main__":
    main()

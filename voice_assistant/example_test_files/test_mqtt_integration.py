#!/usr/bin/env python3
"""
Test MQTT Integration
Tests the complete MQTT integration with the voice assistant actions.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.module_loader import initialize_modules
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_mqtt_integration():
    """Test the MQTT integration with voice assistant actions."""
    print("Testing MQTT Integration with Voice Assistant")
    print("=" * 60)
    
    try:
        # Initialize all modules
        print("Initializing voice assistant modules...")
        modules = initialize_modules("config.yaml")
        
        # Get the actions module
        actions = modules.get('actions')
        if not actions:
            print(" Actions module not found!")
            return
        
        print(" Actions module loaded successfully!")
        print()
        
        # Test MQTT status
        print("MQTT Status:")
        mqtt_status = actions.get_mqtt_status()
        print(f"  Initialized: {mqtt_status.get('initialized', False)}")
        print(f"  Connected: {mqtt_status.get('connected', False)}")
        if mqtt_status.get('broker_host'):
            print(f"  Broker: {mqtt_status['broker_host']}:{mqtt_status.get('broker_port', 1883)}")
        print()
        
        # Test device control actions
        print("Testing Device Control Actions:")
        print("-" * 40)
        
        # Test turn on device
        print("1. Testing turn on device...")
        result1 = actions.execute_action(
            "turn_on_device", 
            {"device": "light", "room": "living_room"}
        )
        print(f"   Result: {result1}")
        print()
        
        # Test turn off device
        print("2. Testing turn off device...")
        result2 = actions.execute_action(
            "turn_off_device", 
            {"device": "fan", "room": "bedroom"}
        )
        print(f"   Result: {result2}")
        print()
        
        # Test with missing device
        print("3. Testing with missing device...")
        result3 = actions.execute_action(
            "turn_on_device", 
            {"room": "kitchen"}
        )
        print(f"   Result: {result3}")
        print()
        
        # Test non-MQTT action (should work regardless)
        print("4. Testing non-MQTT action (greet)...")
        result4 = actions.execute_action(
            "greet", 
            {"name": "User"}
        )
        print(f"   Result: {result4}")
        print()
        
        # Test direct MQTT publishing
        print("5. Testing direct MQTT publishing...")
        mqtt_result = actions.publish_mqtt_message("test/direct", "Hello MQTT!")
        print(f"   MQTT Result: {mqtt_result}")
        print()
        
        print(" All tests completed!")
        
    except Exception as e:
        print(f" Error during testing: {str(e)}")
        logger.exception("Test failed")

if __name__ == "__main__":
    test_mqtt_integration()

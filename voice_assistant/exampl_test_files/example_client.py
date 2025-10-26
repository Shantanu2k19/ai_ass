#!/usr/bin/env python3
"""
Example client script for testing the Voice Assistant Platform API.
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("Health check passed")
            print(f"  Response: {response.json()}")
            return True
        else:
            print(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Health check error: {e}")
        return False

def test_modules_status():
    """Test the modules status endpoint."""
    print("\nTesting modules status...")
    try:
        response = requests.get(f"{BASE_URL}/modules/status")
        if response.status_code == 200:
            print("Modules status retrieved")
            status = response.json()
            for module, info in status.items():
                print(f"  {module}: {info}")
            return True
        else:
            print(f"Modules status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Modules status error: {e}")
        return False

def test_speak():
    """Test the text-to-speech endpoint."""
    print("\nTesting text-to-speech...")
    try:
        data = {
            "text": "Hello, this is a test of the voice assistant platform!",
            "voice": "en-US-Standard-A"
        }
        response = requests.post(f"{BASE_URL}/speak", json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("Text-to-speech working")
                print(f"  Response: {result}")
                return True
            else:
                print(f"Text-to-speech failed: {result}")
                return False
        else:
            print(f"Text-to-speech request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Text-to-speech error: {e}")
        return False

def test_process_intent():
    """Test the intent processing endpoint."""
    print("\nTesting intent processing...")
    try:
        test_phrases = [
            "Hello, how are you?",
            "Turn on the lights",
            "What's the weather like?",
            "Play some music",
            "What time is it?"
        ]
        
        for phrase in test_phrases:
            print(f"  Testing: '{phrase}'")
            data = {
                "text": phrase,
                "context": {}
            }
            response = requests.post(f"{BASE_URL}/process_intent", json=data)
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    intent = result.get("intent", {}).get("intent", "unknown")
                    confidence = result.get("intent", {}).get("confidence", 0)
                    print(f"    Intent: {intent} (confidence: {confidence:.2f})")
                else:
                    print(f"    Failed: {result}")
            else:
                print(f"    Request failed: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"Intent processing error: {e}")
        return False

def test_light_control():
    """Test light control actions."""
    print("\nTesting light control...")
    try:
        # Test turning on lights
        data = {
            "text": "Turn on the living room lights",
            "context": {}
        }
        response = requests.post(f"{BASE_URL}/process_intent", json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                action_result = result.get("action", {})
                print("Light control working")
                print(f"  Action result: {action_result}")
                return True
            else:
                print(f"Light control failed: {result}")
                return False
        else:
            print(f"Light control request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Light control error: {e}")
        return False

def main():
    """Run all client tests."""
    print("Voice Assistant Platform - Client Test")
    print("=" * 45)
    
    tests = [
        test_health,
        test_modules_status,
        test_speak,
        test_process_intent,
        test_light_control
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(0.5)  # Small delay between tests
    
    print("\n" + "=" * 45)
    print(f"Client Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All client tests passed! The API is working correctly.")
    else:
        print("Some client tests failed. Please check the server logs.")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())


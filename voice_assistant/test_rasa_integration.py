#!/usr/bin/env python3
"""
Test script to verify Rasa integration in the voice assistant.
"""

import requests
import json

def test_rasa_integration():
    """Test the Rasa integration via the voice assistant API."""
    
    # Test data
    test_cases = [
        "Hello there",
        "Turn on the light",
        "Turn off the fan",
        "What time is it?",
        "What day is today?",
        "What's the date?"
    ]
    
    print("=" * 60)
    print("TESTING RASA INTEGRATION VIA VOICE ASSISTANT API")
    print("=" * 60)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{text}'")
        print("-" * 40)
        
        try:
            # Make request to the voice assistant
            response = requests.post(
                "http://localhost:8000/process_intent",
                json={
                    "text": text,
                    "context": {}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Status: {response.status_code}")
                print(f"   ✅ Intent: {result.get('intent', 'N/A')}")
                print(f"   ✅ Confidence: {result.get('confidence', 0):.3f}")
                print(f"   ✅ Entities: {result.get('entities', {})}")
                print(f"   ✅ Success: {result.get('success', False)}")
            else:
                print(f"   ❌ Error: HTTP {response.status_code}")
                print(f"   ❌ Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Error: Cannot connect to voice assistant server")
            print("   💡 Make sure the server is running on localhost:8000")
            break
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_rasa_integration()

#!/usr/bin/env python3
"""
Test script to verify the voice assistant platform setup.
"""

import sys
import os
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from app.core.config import Config
        from app.core.module_loader import initialize_modules
        print("✓ Core modules imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import core modules: {e}")
        return False
    
    try:
        from app.modules.tts.base import BaseTTS
        from app.modules.stt.base import BaseSTT
        from app.modules.intent.base import BaseIntent
        from app.modules.actions.base import BaseActions
        print("✓ Base module classes imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import base classes: {e}")
        return False
    
    try:
        from app.modules.tts.google_tts import GoogleTTS
        from app.modules.stt.whisper_stt import WhisperSTT
        from app.modules.intent.llm_intent import LLMIntent
        from app.modules.actions.light_control import LightControl
        print("✓ Concrete module implementations imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import concrete implementations: {e}")
        return False
    
    return True

def test_config_loading():
    """Test configuration loading."""
    print("\nTesting configuration loading...")
    
    try:
        from app.core.config import Config
        config = Config("config.yaml")
        print("✓ Configuration loaded successfully")
        
        # Test getting module configs
        tts_config = config.get_module_config("tts")
        stt_config = config.get_module_config("stt")
        intent_config = config.get_module_config("intent")
        actions_config = config.get_module_config("actions")
        
        print(f"  TTS: {tts_config}")
        print(f"  STT: {stt_config}")
        print(f"  Intent: {intent_config}")
        print(f"  Actions: {actions_config}")
        
        return True
    except Exception as e:
        print(f"✗ Failed to load configuration: {e}")
        return False

def test_module_loading():
    """Test dynamic module loading."""
    print("\nTesting module loading...")
    
    try:
        from app.core.module_loader import initialize_modules
        modules = initialize_modules()
        print("✓ Modules loaded successfully")
        
        for module_name, module in modules.items():
            print(f"  {module_name}: {type(module).__name__}")
        
        return True
    except Exception as e:
        print(f"✗ Failed to load modules: {e}")
        return False

def test_module_functionality():
    """Test basic module functionality."""
    print("\nTesting module functionality...")
    
    try:
        from app.core.module_loader import initialize_modules
        modules = initialize_modules()
        
        # Initialize modules
        for module_name, module in modules.items():
            if hasattr(module, 'initialize'):
                success = module.initialize()
                if success:
                    print(f"✓ {module_name} initialized successfully")
                else:
                    print(f"✗ {module_name} failed to initialize")
                    return False
        
        # Test TTS
        if "tts" in modules:
            tts = modules["tts"]
            result = tts.speak("Hello, this is a test")
            if result.get("success"):
                print("✓ TTS module working")
            else:
                print(f"✗ TTS module failed: {result}")
                return False
        
        # Test STT
        if "stt" in modules:
            stt = modules["stt"]
            result = stt.transcribe(b"mock audio data")
            if result.get("success"):
                print("✓ STT module working")
            else:
                print(f"✗ STT module failed: {result}")
                return False
        
        # Test Intent
        if "intent" in modules:
            intent = modules["intent"]
            result = intent.recognize_intent("Hello, how are you?")
            if result.get("success"):
                print("✓ Intent module working")
            else:
                print(f"✗ Intent module failed: {result}")
                return False
        
        # Test Actions
        if "actions" in modules:
            actions = modules["actions"]
            result = actions.execute_action("light_control", {"device": "living_room", "action": "toggle"})
            if result.get("success"):
                print("✓ Actions module working")
            else:
                print(f"✗ Actions module failed: {result}")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Module functionality test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Voice Assistant Platform - Setup Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_config_loading,
        test_module_loading,
        test_module_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The voice assistant platform is ready to use.")
        print("\nTo start the server, run:")
        print("  python -m app.main")
        print("\nOr visit http://localhost:8000/docs for API documentation")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())


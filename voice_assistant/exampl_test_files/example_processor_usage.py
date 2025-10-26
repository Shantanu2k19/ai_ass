#!/usr/bin/env python3
"""
Example usage of the RequestProcessor for intent -> action -> response pipeline.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.module_loader import ModuleLoader
from app.core.config import Config
from app.core.processor import RequestProcessor

def main():
    """Example of using the RequestProcessor."""
    
    print("Initializing Voice Assistant modules...")
    
    # Load all modules
    config = Config("config.yaml")
    loader = ModuleLoader(config)
    modules = loader.load_all_modules()
    
    print(f"Loaded modules: {list(modules.keys())}")
    
    # Example texts to test
    test_texts = [
        "Hello there",
        "Turn on the light",
        "Turn off the fan in bedroom", 
        "What time is it?",
        "What day is today?",
        "What's the date?",
        "This is something random"
    ]
    
    print("\n" + "="*60)
    print("PROCESSING EXAMPLES")
    print("="*60)
    
    for text in test_texts:
        print(f"\nInput: '{text}'")
        print("-" * 40)
        
        try:
            # Create processor instance
            processor = RequestProcessor(
                text=text,
                intent_module=modules['local_intent'],
                llm_intent=modules['llm_intent'], 
                action_module=modules['actions'],
                tts_module=modules['tts']
            )
            
            # Process complete pipeline
            response = processor.process_complete()
            
            # Display results
            print(f"Intent: {processor.intent}")
            print(f"Confidence: {processor.confidence:.3f}")
            print(f"Entities: {processor.entities}")
            print(f"Actionable: {processor.actionable_command}")
            
            if processor.action_result:
                print(f"Action Result: {processor.action_result}")
            
            print(f"Response: {response.get('text', 'No response')}")
            
        except Exception as e:
            print(f"Error processing '{text}': {str(e)}")
    
    print("\n" + "="*60)
    print("PROCESSING COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()

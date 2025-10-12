
import os
import json
import asyncio
from typing import Dict, List, Any

# Import for Rasa 3.x using Agent
from rasa.core.agent import Agent

MODEL_PATH = "/home/212186@HTMEDIA.NET/Desktop/ai_ass/rasa_nlu/models"

class RasaInference:
    def __init__(self, model_path: str = None):
        """
        Initialize Rasa inference with the latest model.
        
        Args:
            model_path: Path to the models directory. If None, uses MODEL_PATH.
        """
        self.model_path = model_path or MODEL_PATH
        self.agent = None
        self.load_latest_model()
    
    def load_latest_model(self):
        """Load the latest NLU model from the models directory."""
        try:
            # Get all model files and sort by modification time
            model_files = [f for f in os.listdir(self.model_path) if f.endswith('.tar.gz')]
            if not model_files:
                raise FileNotFoundError("No model files found in the models directory")
            
            # Sort by modification time (newest first)
            model_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.model_path, x)), reverse=True)
            latest_model = model_files[0]
            
            model_full_path = os.path.join(self.model_path, latest_model)
            print(f"Loading model: {latest_model}")
            
            # Load the model using Agent (Rasa 3.x)
            self.agent = Agent.load(model_full_path)
            print(f"Model loaded successfully!")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    
    async def predict_intent(self, text: str) -> Dict[str, Any]:
        """
        Predict intent and entities from text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary containing intent, confidence, and entities
        """
        if not self.agent:
            raise RuntimeError("Model not loaded. Call load_latest_model() first.")
        
        try:
            result = await self.agent.parse_message(text)
            return result
        except Exception as e:
            print(f"Error during prediction: {e}")
            raise
    
    async def get_intent_confidence(self, text: str) -> tuple:
        """
        Get intent and confidence score.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Tuple of (intent_name, confidence_score)
        """
        result = await self.predict_intent(text)
        intent = result.get('intent', {})
        return intent.get('name', 'unknown'), intent.get('confidence', 0.0)
    
    async def get_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract entities from text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of entity dictionaries
        """
        result = await self.predict_intent(text)
        return result.get('entities', [])
    
    async def batch_predict(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Predict intents for multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of prediction results
        """
        results = []
        for text in texts:
            try:
                result = await self.predict_intent(text)
                results.append(result)
            except Exception as e:
                print(f"Error processing '{text}': {e}")
                results.append({'error': str(e), 'text': text})
        return results

async def main():
    """Example usage of the RasaInference class."""
    try:
        # Initialize the inference class
        rasa_inference = RasaInference()
        
        # Example texts to test
        test_texts = [
            "Hello there",
            "Turn on the light",
            "Turn off the fan",
            "What time is it?",
            "What day is today?",
            "What's the date?",
            "This is something random"
        ]
        
        print(f"=" * 50)
        print(f"RASA NLU INFERENCE RESULTS")
        print(f"=" * 50)
        
        for text in test_texts:
            print(f"\nText: '{text}'")
            print(f"-" * 30)
            
            # Get intent and confidence
            intent, confidence = await rasa_inference.get_intent_confidence(text)
            print(f"Intent: {intent}")
            print(f"Confidence: {confidence:.3f}")
            
            # Get entities
            entities = await rasa_inference.get_entities(text)
            if entities:
                print(f"Entities: {entities}")
            else:
                print(f"Entities: None")
        
        print(f"\n" + "=" * 50)
        print(f"BATCH PREDICTION EXAMPLE")
        print(f"=" * 50)
        
        # Batch prediction example
        batch_results = await rasa_inference.batch_predict(test_texts[:3])
        for i, result in enumerate(batch_results):
            if 'error' not in result:
                intent = result.get('intent', {}).get('name', 'unknown')
                confidence = result.get('intent', {}).get('confidence', 0.0)
                print(f"Text {i+1}: Intent='{intent}', Confidence={confidence:.3f}")
            else:
                print(f"Text {i+1}: Error - {result['error']}")
                
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == "__main__":
    asyncio.run(main())

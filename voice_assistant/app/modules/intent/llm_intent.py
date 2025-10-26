import os
import json
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from .base import BaseIntent
from app.modules.intent.intents import ALL_INTENTS
load_dotenv()


class LLMIntent(BaseIntent):
    """LLM-based Intent Recognition implementation."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.supported_intents = ALL_INTENTS
        self.config = config or {}
        
        # API configurations
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.openai_api_url = "https://api.openai.com/v1/chat/completions"
        self.gemini_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        
        # LLM configuration from config file
        self.llm_config = self.config.get('settings', {}).get('llm', {})
        self.provider = self.llm_config.get('provider', 'chatgpt')
        
        # Available actions will be fetched dynamically
        self.available_actions = {}
        self.actions_module = None
    
    def fetch_available_actions(self) -> Dict[str, str]:
        """Fetch available actions from the actions module."""
        try:
            from app.modules.actions.all_actions import Actions
            temp_actions = Actions()
            available_actions = temp_actions.get_available_actions()
            
            # Create descriptions for each action
            action_descriptions = {
                "greet": "Respond to greetings like 'hello', 'hi', 'good morning'",
                "turn_on_device": "Turn on devices like lights, fans, AC, etc. (requires device name)",
                "turn_off_device": "Turn off devices like lights, fans, AC, etc. (requires device name)",
                "ask_time": "Get current time when asked 'what time is it', 'current time'",
                "ask_day": "Get current day when asked 'what day is it', 'today'",
                "ask_date": "Get current date when asked 'what date is it', 'today's date'",
                "out_of_scope": "For requests that don't match any available actions"
            }
            
            # Filter to only include actions that are available
            self.available_actions = {
                action: action_descriptions.get(action, f"Handle {action} intent")
                for action in available_actions
                if action in action_descriptions
            }
            
            self.logger.info(f"Fetched {len(self.available_actions)} available actions")
            return self.available_actions
            
        except Exception as e:
            self.logger.error(f"Failed to fetch available actions: {str(e)}")
            self.available_actions = {
                "greet": "Respond to greetings",
                "turn_on_device": "Turn on devices",
                "turn_off_device": "Turn off devices",
                "ask_time": "Get current time",
                "ask_day": "Get current day",
                "ask_date": "Get current date",
                "out_of_scope": "Handle unrecognized requests"
            }
            return self.available_actions

    def initialize(self) -> bool:
        """Initialize LLM intent recognition engine."""
        try:
            if not self._check_provider_availability(self.provider):
                self.logger.error(f"API key not found for configured provider: {self.provider}")
                return False
            
            self.logger.info(f"Using LLM provider: {self.provider}")
            
            self.fetch_available_actions()
                
            self.logger.info("Initializing LLM Intent Recognition...")
            self.is_initialized = True
            self.logger.info("LLM Intent Recognition initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM Intent: {str(e)}")
            return False

    def _check_provider_availability(self, provider: str) -> bool:
        """Check if a specific LLM provider is available."""
        if provider == "chatgpt":
            return bool(self.openai_api_key)
        elif provider == "gemini":
            return bool(self.gemini_api_key)
        return False
    
    def _create_prompt(self, text: str) -> str:
        """Create a structured prompt for LLM intent recognition."""
        actions_list = "\n".join([f"- {intent}: {description}" for intent, description in self.available_actions.items()])
        
        prompt = f"""You are a voice assistant that can either control devices or answer questions directly.

        AVAILABLE DEVICE ACTIONS:
        {actions_list}

        TASK: For "{text}" - either match a device action OR provide a direct spoken response.

        RULES:
        1. If it's a device control request (lights, fans, time, etc.) → use matching intent
        2. If it's a general question/information request → provide direct answer
        3. If request cannot be completed → give helpful response
        4. Always be conversational and helpful

        RESPONSE FORMAT (JSON only):
        For device control: {{"intent": "action_name", "confidence": 0.95, "entities": {{"device": "lights"}}, "reasoning": "brief reason"}}
        For general questions: {{"intent": "direct_response", "confidence": 1.0, "entities": {{}}, "reasoning": "general question", "speech_response": "Your spoken answer here"}}

        User: "{text}"
        AI Assistant Response:"""
        return prompt

    def _call_chatgpt_api(self, prompt: str) -> Dict[str, Any]:
        """Call ChatGPT API for intent recognition."""
        try:
            if not self.openai_api_key:
                raise Exception("OpenAI API key not available")
                
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are an AI assistant for intent recognition. Respond with JSON only. Be concise."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1
            }
            
            response = requests.post(self.openai_api_url, headers=headers, json=data, timeout=5)
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse ChatGPT response as JSON, using fallback")
                return {
                    "intent": "out_of_scope",
                    "confidence": 0.5,
                    "entities": {},
                    "reasoning": "Failed to parse response"
                }
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"ChatGPT API request failed: {str(e)}")
            return {
                "intent": "out_of_scope",
                "confidence": 0.3,
                "entities": {},
                "reasoning": f"API error: {str(e)}"
            }
        except Exception as e:
            self.logger.error(f"Unexpected error in ChatGPT API call: {str(e)}")
            return {
                "intent": "out_of_scope",
                "confidence": 0.3,
                "entities": {},
                "reasoning": f"Unexpected error: {str(e)}"
            }

    def _call_gemini_api(self, prompt: str) -> Dict[str, Any]:
        """Call Gemini API for intent recognition."""
        try:
            if not self.gemini_api_key:
                raise Exception("Gemini API key not available")
                
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.gemini_api_key
            }
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.1
                }
            }
            
            response = requests.post(self.gemini_api_url, headers=headers, json=data, timeout=5)
            response.raise_for_status()
            

            result = response.json()
            # self.logger.info(f"resp:{result}")
            
            # Check if response has content
            candidate = result["candidates"][0]
            if "content" not in candidate or "parts" not in candidate["content"]:
                self.logger.warning("Gemini response has no content")
                return {
                    "intent": "out_of_scope",
                    "confidence": 0.3,
                    "entities": {},
                    "reasoning": "No content in response"
                }
            
            content = candidate["content"]["parts"][0]["text"].strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse Gemini response as JSON, using fallback")
                return {
                    "intent": "out_of_scope",
                    "confidence": 0.5,
                    "entities": {},
                    "reasoning": "Failed to parse response"
                }
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Gemini API request failed: {str(e)}")
            return {
                "intent": "out_of_scope",
                "confidence": 0.3,
                "entities": {},
                "reasoning": f"API error: {str(e)}"
            }
        except Exception as e:
            self.logger.error(f"Unexpected error in Gemini API call: {str(e)}")
            return {
                "intent": "out_of_scope",
                "confidence": 0.3,
                "entities": {},
                "reasoning": f"Unexpected error: {str(e)}"
            }

    def recognize_intent(self, text: str, **kwargs) -> Dict[str, Any]:
        """Recognize intent from text using configured LLM provider."""
        if not self.is_initialized:
            return {"error": "LLM Intent not initialized", "success": False}
        
        try:
            self.logger.info(f"LLM analyzing: '{text}'")
            prompt = self._create_prompt(text)
            
            self.logger.info(f"Attempting intent recognition with {self.provider}...")
            result = self._call_llm_provider(self.provider, prompt)
            return self._process_result(result, text, self.provider)
            
        except Exception as e:
            self.logger.error(f"LLM Intent error: {str(e)}")
            return {
                "error": str(e), 
                "success": False,
                "intent": "out_of_scope",
                "confidence": 0.1
            }

    def _call_llm_provider(self, provider: str, prompt: str) -> Dict[str, Any]:
        """Call the specified LLM provider."""
        if provider == "chatgpt":
            return self._call_chatgpt_api(prompt)
        elif provider == "gemini":
            return self._call_gemini_api(prompt)
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")

    def _process_result(self, result: Dict[str, Any], text: str, model: str) -> Dict[str, Any]:
        """Process and validate the LLM result."""
        try:
            intent = result.get("intent", "direct_response")
            confidence = float(result.get("confidence", 0.5))
            entities = result.get("entities", {})
            reasoning = result.get("reasoning", "")
            speech_response = result.get("speech_response", "")
            
            # Handle direct response (general questions)
            if intent == "direct_response":
                self.logger.info(f"LLM direct response: {speech_response}")
                return {
                    "success": True,
                    "intent": "direct_response",
                    "confidence": confidence,
                    "entities": entities,
                    "text": text,
                    "model": model,
                    "reasoning": reasoning,
                    "speech_response": speech_response
                }
            
            # Handle device control intents
            if intent not in self.supported_intents:
                # If intent not supported, treat as direct response
                self.logger.info(f"Unsupported intent '{intent}', treating as direct response")
                return {
                    "success": True,
                    "intent": "direct_response",
                    "confidence": 0.8,
                    "entities": {},
                    "text": text,
                    "model": model,
                    "reasoning": f"Intent '{intent}' not supported, providing direct response",
                    "speech_response": "I'm sorry, I can't help with that specific request right now."
                }
            
            self.logger.info(f"LLM reasoning: {reasoning}")
            
            return {
                "success": True,
                "intent": intent,
                "confidence": confidence,
                "entities": entities,
                "text": text,
                "model": model,
                "reasoning": reasoning
            }
            
        except Exception as e:
            self.logger.error(f"Error processing LLM result: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "intent": "direct_response",
                "confidence": 0.1,
                "speech_response": "I'm sorry, I encountered an error processing your request."
            }
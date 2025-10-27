import uuid
import time
from datetime import datetime
from app.modules.intent.intents import OUT_OF_SCOPE, ALL_INTENTS
from app.constants import INTENT_CONFIDENCE_THRESHOLD
import logging as log 
logger = log.getLogger(__name__)


class RequestProcessor():

    def __init__(self, text, intent_module, llm_intent, action_module, tts_module, db_handler=None) -> None:
        # input 
        self.text = text 
        self.context = {} 

        # modules 
        self.intent_module = intent_module
        self.llm_module = llm_intent
        self.action_module = action_module
        self.tts_module = tts_module
        self.db_handler = db_handler

        # output data
        self.intent = None
        self.entities = None 
        self.confidence = None 
        self.action_result = None

        self.actionable_command = False
        self.speech_text = None

        # logger 
        self.log_tag = f"[{str(uuid.uuid4())[:4]}]"
        
        # Database logging data
        self.request_time = datetime.now().isoformat()
        self.start_time = time.time()
        self.intent_source = None  # 'rasa' or 'llm'
        self.action_executed = False
        self.action_success = False
        self.had_error = False
        self.error_message = None

    
    def process_intent(self):
        """Recognize intent using Rasa or LLM fallback."""
        try:
            # Rasa intent recognition
            intent_result = self.intent_module.recognize_intent(self.text, **self.context)
            
            self.intent = intent_result.get("intent", "")
            self.confidence = intent_result.get("confidence", 0)
            self.entities = intent_result.get("entities", {})
            self.intent_source = 'rasa'
            
            logger.info(f"{self.log_tag} RASA: Intent[{self.intent}] confidence[{self.confidence}]")

            # If Rasa returns out_of_scope or low confidence, use LLM fallback
            if self.intent == OUT_OF_SCOPE or self.confidence <= INTENT_CONFIDENCE_THRESHOLD: 
                logger.info(f"{self.log_tag} LLM intent fallback")
                
                intent_result = self.llm_module.recognize_intent(self.text, **self.context)
                self.intent = intent_result.get("intent", "")
                self.confidence = intent_result.get("confidence", 0)
                self.entities = intent_result.get("entities", {})
                self.intent_source = 'llm'
                
                # Handle direct response from LLM
                if self.intent == "direct_response":
                    self.speech_text = intent_result.get("speech_response", "I'm sorry, I couldn't process that request.")
                    self.actionable_command = False
                    logger.info(f"{self.log_tag} LLM Direct Response: {self.speech_text}")
                else:
                    logger.info(f"{self.log_tag} LLM: Intent[{self.intent}]")
        except Exception as e:
            logger.error(f"{self.log_tag} Intent error: {e}")
            self.had_error = True
            self.error_message = str(e)
            self.intent = "error"
            self.intent_source = 'error'

        return 

    def _determine_actionable_command(self):
        """Determine if the current intent requires action execution."""
        # List of intents that require action execution
        actionable_intents = [
            "greet", "turn_on_device", "turn_off_device", 
            "ask_time", "ask_day", "ask_date", "out_of_scope"
        ]
        
        # Direct responses don't need action execution
        if self.intent == "direct_response":
            self.actionable_command = False
            logger.info(f"{self.log_tag} Direct response - no action required")
        else:
            # Set actionable_command based on intent
            self.actionable_command = self.intent in actionable_intents
            logger.info(f"{self.log_tag} Actionable command: {self.actionable_command} for intent: {self.intent}")

    def process_action(self):
        """Execute action based on detected intent."""
        # Skip action execution for direct responses
        if self.intent == "direct_response":
            logger.info(f"{self.log_tag} Direct response - skipping action")
            return
            
        if self.intent not in ALL_INTENTS:
            logger.info(f"{self.log_tag} No action required for intent: {self.intent}")
            return

        logger.info(f"{self.log_tag} Executing action: {self.intent}")
        
        try:
            self.action_executed = True
            action_result = self.action_module.execute_action(self.intent, self.entities, **self.context)
            self.action_success = action_result.get('success', False)
            
            # Update speech text if action provides one
            if action_result.get('speech_op'):
                self.speech_text = action_result.get('speech_op')
                logger.info(f"{self.log_tag} Action speech: {self.speech_text}")
                
        except Exception as e:
            logger.error(f"{self.log_tag} Action error: {e}")
            self.action_executed = True
            self.action_success = False
            self.speech_text = "Something went wrong. Try again later."
            self.had_error = True
            self.error_message = f"Action error: {str(e)}"
        
        return

    def process_speechresponse(self, fallback_text=None):
        """Generate speech response and save to database."""
        if fallback_text:
            self.speech_text = fallback_text
                
        if not self.speech_text:
            self.speech_text = "Something went wrong. Try again later."
        
        # Generate TTS audio
        if self.tts_module:
            try:
                tts_result = self.tts_module.speak(self.speech_text)
                if not tts_result.get("success", False):
                    self.had_error = True
                    self.error_message = f"TTS error: {tts_result.get('error', 'Unknown')}"
            except Exception as e:
                logger.error(f"{self.log_tag} TTS error: {e}")
                self.had_error = True
                self.error_message = f"TTS error: {str(e)}"
        
        # Save to database
        self.save_to_db()
        return { "success": True }

    def save_to_db(self):
        """Save request data to database."""
        if not self.db_handler:
            return
        
        try:
            total_time = time.time() - self.start_time
            
            self.db_handler.log_request({
                'request_time': self.request_time,
                'text': self.text,
                'intent': self.intent,
                'intent_source': self.intent_source,
                'action_executed': self.action_executed,
                'action_success': self.action_success,
                'tts_text': self.speech_text,
                'total_time': total_time,
                'had_error': self.had_error,
                'error_message': self.error_message
            })
                
        except Exception as e:
            logger.error(f"{self.log_tag} Error saving to database: {e}")

    
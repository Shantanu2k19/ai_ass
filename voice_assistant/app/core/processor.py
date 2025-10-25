import uuid
from app.modules.intent.intents import OUT_OF_SCOPE, ALL_INTENTS
from app.constants import INTENT_CONFIDENCE_THRESHOLD
import logging as log 
logger = log.getLogger(__name__)


class RequestProcessor():

    def __init__(self, text, intent_module, llm_intent, action_module, tts_module) -> None:
        # input 
        self.text = text 
        self.context = {} 

        # modules 
        self.intent_module = intent_module
        self.llm_module = llm_intent
        self.action_module = action_module
        self.tts_module = tts_module

        # output data
        self.intent = None
        self.entities = None 
        self.confidence = None 
        self.action_result = None

        self.actionable_command = False
        self.speech_text = None

        # logger 
        self.log_tag = f"[{str(uuid.uuid4())[:4]}]"

    
    def process_intent(self):
        # Use LLM as primary intent recognizer
        logger.info(f"{self.log_tag} Using LLM for intent recognition")
        
        intent_result = self.llm_module.recognize_intent(self.text, **self.context)
        
        # Update with LLM results
        self.intent = intent_result.get("intent", "")
        self.confidence = intent_result.get("confidence", 0)
        self.entities = intent_result.get("entities", {})
        
        # Handle direct response from LLM
        if self.intent == "direct_response":
            self.speech_text = intent_result.get("speech_response", "I'm sorry, I couldn't process that request.")
            self.actionable_command = False
            logger.info(f"{self.log_tag} LLM Direct Response: {self.speech_text}")
        else:
            logger.info(f"{self.log_tag} LLM Intent[{self.intent}] confidence[{self.confidence}] entities[{self.entities}]")
        
        self.save_to_db()

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
            logger.info(f"{self.log_tag} Direct response - skipping action execution")
            # Preserve the speech_text from LLM response
            logger.info(f"{self.log_tag} Preserving speech text: {self.speech_text}")
            return
            
        if self.intent not in ALL_INTENTS:
            logger.info(f"{self.log_tag} No action required for intent: {self.intent}")
            return

        logger.info(f"{self.log_tag} Executing action for intent: {self.intent}")
        
        try:
            action_result = self.action_module.execute_action(self.intent, self.entities, **self.context)
            
            logger.info(f"{self.log_tag} Action result: {action_result}")
            
            # Store action result for potential use in speech response
            self.action_result = action_result.get('success', False)
            
            # Only update speech_text if action provides one
            if action_result.get('speech_op'):
                self.speech_text = action_result.get('speech_op')
                logger.info(f"{self.log_tag} Action provided speech: {self.speech_text}")
            
            if self.action_result == False:
                self.speech_text = "Something went wrong. Try again later."
                self.save_to_db()
            else:
                logger.warning(f"{self.log_tag} Action execution failed: {action_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"{self.log_tag} Action execution error: {str(e)}")
            self.speech_text = "Something went wrong. Try again later."
            self.action_result = False
        
        return

    def process_speechresponse(self):
        """Generate speech response based on action result or provided text."""
        if not self.speech_text:
            self.speech_text = "Something went wrong. Try again later."
        
        # Generate TTS audio if TTS module is available
        if self.tts_module:
            try:
                tts_result = self.tts_module.speak(self.speech_text)
                if tts_result.get("success", False):
                    logger.info(f"{self.log_tag} TTS audio generated successfully")
                    return { "success": True }
                else:
                    logger.warning(f"{self.log_tag} TTS generation failed: {tts_result.get('error')}")
            except Exception as e:
                logger.error(f"{self.log_tag} TTS error: {str(e)}")
        
        return { "success": True }

    def save_to_db(self):
        # TODO
        pass

    
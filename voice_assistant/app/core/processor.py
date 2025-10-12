import uuid
from app.modules.intent.intents import OUT_OF_SCOPE
from constants import INTENT_CONFIDENCE_THRESHOLD
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

        self.actionable_command = False

        # logger 
        self.log_tag = f"[{str(uuid.uuid4())[:4]}]"

    
    def process_intent(self):
        intent_result = self.intent_module.recognize_intent(self.text, **self.context)

        self.intent = intent_result.get("intent", "")
        self.confidence = intent_result.get("confidence", 0)
        self.entities = intent_result.get("entities", {})

        logger.info(f"{self.log_tag} Intent[{self.intent}] confidence[{self.confidence}] entities[{self.entities}]")

        if self.intent == OUT_OF_SCOPE or self.confidence <= INTENT_CONFIDENCE_THRESHOLD: 
            logger.info(f"{self.log_tag} LLM intent fallback")
            
            intent_result = self.llm_module.recognize_intent(self.text, **self.context)

            #TODO 
        
        #  self.actionable_command = True
        
        self.save_to_db()
        return

    def process_action(self):
        if not self.actionable_command:
            return 

        process_action_result = self.action_module.execute_action(self.intent, self.entities, **self.context)

        logger.info(f"{self.log_tag} Action[{self.action}] result[{process_action_result}]")

        if process_action_result.get("success", False):
            self.save_to_db()
        return

    def process_speechresponse(self, text: str=None):
        pass

    def save_to_db(self):
        # TODO
        pass

    
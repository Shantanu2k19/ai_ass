"""
Main FastAPI application for the modular voice assistant platform.
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

from app.core.module_loader import initialize_modules, ModuleLoader
from app.core.config import Config
from app.core.processor import RequestProcessor
# Load configuration
config = Config()

# Configure logging from config
logging_config = config.get_setting('settings', {}).get('logging', {})
log_level = getattr(logging, logging_config.get('level', 'INFO').upper())
log_format = logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logging.basicConfig(
    level=log_level,
    format=log_format
)
logger = logging.getLogger(__name__)

# Global variables for modules
modules: Dict[str, Any] = {}
config: Optional[Config] = None
module_loader: Optional[ModuleLoader] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application lifespan events."""
    global modules, config, module_loader
    
    # Startup
    try:
        logger.info("Starting ===============")
        
        # Load config and Init modules 
        config = Config("config.yaml")
        module_loader = ModuleLoader(config)
        modules = module_loader.load_all_modules()
        
        # Initialize all modules
        for module_name, module in modules.items():
            if hasattr(module, 'initialize'):
                success = module.initialize()
                if not success:
                    logger.error(f"Failed to initialize module '{module_name}'")
        
        logger.info("Init done ===============")
        
    except Exception as e:
        logger.error(f"Failed to start Voice Assistant Platform: {str(e)}")
        raise
    
    yield
    
    # Shutdown (if needed)
    logger.info("Shutting down Voice Assistant Platform...")


# Initialize FastAPI app
app = FastAPI(
    title="Voice Assistant Platform",
    description="A modular voice assistant platform with pluggable TTS, STT, Intent, and Action modules",
    version="1.0.0",
    lifespan=lifespan
)

class ProcessIntentRequest(BaseModel):
    """Request model for intent processing."""
    text: str
    context: Optional[Dict[str, Any]] = None


@app.get("/")
async def home():
    """Home endpoint."""
    return {
        "message": "Hello from AI_ASS"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "modules_loaded": len(modules),
        "available_modules": list(modules.keys())
    }

@app.post("/process_intent")
async def process_intent(request: ProcessIntentRequest):
    """
    Process text through intent recognition and action execution.
    """
    try:
        text = request.text
        context = request.context or {}
        
        logger.info(f"Processing intent for text: '{text}'")
        
        intent_module = modules.get('local_intent', None)
        llm_intent = modules.get('llm_intent', None)
        action_module = modules.get('actions', None)
        tts_module = modules.get('tts', None)

        if not intent_module or not action_module or not tts_module:
            return {"error": f"Missing required modules: intent[{intent_module}] action[{action_module}] tts[{tts_module}]", "success": False}

        #request processing pipeling 
        request_processor = RequestProcessor(text, intent_module, llm_intent, action_module, tts_module)

        try:
            # intent 
            request_processor.process_intent()

            # action
            request_processor.process_action()

            # speech response 
            request_processor.process_speechresponse()
            
            return { "success": True }
        except Exception as ex: 
            request_processor.process_speechresponse("Sorry. Something went wrong.")
            return { "success": False , "mssg": str(ex)[:900]}
        
    except Exception as e:
        logger.error(f"Error processing intent: {str(e)}")
        return {
            "success": False,
            "mssg": str(e)[:900]
        }

# test APIs

class TTSRequest(BaseModel):
    """Request model for TTS testing."""
    text: str
    voice: Optional[str] = None
    language: Optional[str] = None

class IntentTestRequest(BaseModel):
    """Request model for intent recognition testing."""
    text: str
    context: Optional[Dict[str, Any]] = None

@app.post("/test/tts")
async def test_tts(request: TTSRequest):
    """
    Simple TTS API - send text and hear output.
    """
    try:
        tts_module = modules.get('tts', None)
        
        if not tts_module:
            return {
                "success": False,
                "error": "TTS module not available"
            }
        
        logger.info(f"Speaking text: '{request.text}'")
        
        # Prepare TTS parameters
        tts_params = {}
        if request.voice:
            tts_params['voice'] = request.voice
        if request.language:
            tts_params['language'] = request.language
            
        # Call TTS module to generate and play audio
        result = tts_module.speak(request.text, **tts_params)
        
        # Check if TTS was successful
        if result.get('success', False):
            return {
                "success": True,
                "message": f"Spoke: '{request.text}'"
            }
        else:
            return {
                "success": False,
                "error": result.get('error', 'TTS failed')
            }
        
    except Exception as e:
        logger.error(f"Error in TTS: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/test/intent")
async def test_intent(request: IntentTestRequest):
    """
    Test intent recognition module by analyzing text for intent.
    """
    try:
        intent_module = modules.get('local_intent', None)
        llm_intent_module = modules.get('llm_intent', None)
        
        if not intent_module and not llm_intent_module:
            return {
                "success": False,
                "error": "No intent recognition modules available"
            }
        
        logger.info(f"Testing intent recognition with text: '{request.text}'")
        
        results = {}
        
        # Test local intent module if available
        if intent_module:
            try:
                local_result = intent_module.recognize_intent(request.text)
                results['local_intent'] = local_result
            except Exception as e:
                results['local_intent'] = {"error": str(e)}
        
        # Test LLM intent module if available
        if llm_intent_module:
            try:
                llm_result = llm_intent_module.recognize_intent(request.text)
                results['llm_intent'] = llm_result
            except Exception as e:
                results['llm_intent'] = {"error": str(e)}
        
        return {
            "success": True,
            "text": request.text,
            "context": request.context,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error testing intent recognition: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

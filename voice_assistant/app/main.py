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


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

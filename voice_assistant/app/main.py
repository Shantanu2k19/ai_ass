"""
Main FastAPI application for the modular voice assistant platform.
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

from app.core.module_loader import initialize_modules, ModuleLoader
from app.core.config import Config

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

# Initialize FastAPI app
app = FastAPI(
    title="Voice Assistant Platform",
    description="A modular voice assistant platform with pluggable TTS, STT, Intent, and Action modules",
    version="1.0.0"
)

# Global variables for modules
modules: Dict[str, Any] = {}
config: Optional[Config] = None
module_loader: Optional[ModuleLoader] = None


class ProcessAudioRequest(BaseModel):
    """Request model for audio processing."""
    text: Optional[str] = None
    language: Optional[str] = "en"
    voice: Optional[str] = None


class ProcessIntentRequest(BaseModel):
    """Request model for intent processing."""
    text: str
    context: Optional[Dict[str, Any]] = None


@app.on_event("startup")
def startup_event():
    """Initialize modules on startup."""
    global modules, config, module_loader
    
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


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "modules_loaded": len(modules),
        "available_modules": list(modules.keys())
    }


@app.get("/")
async def home():
    """Home endpoint."""
    return {
        "message": "Hello from AI_ASS"
    }

@app.get("/modules/status")
async def get_modules_status():
    """Status of all loaded modules."""
    status = {}
    for module_name, module in modules.items():
        if hasattr(module, 'get_status'):
            status[module_name] = module.get_status()
        else:
            status[module_name] = {"status": "unknown"}
    
    return status


@app.post("/process_audio")
async def process_audio(
    audio_file: UploadFile = File(...),
    language: str = Form("en"),
    voice: Optional[str] = Form(None)
):
    """
    Process audio file through the complete pipeline:
    1. STT: Convert audio to text
    2. Intent: Recognize intent from text
    3. Actions: Execute action based on intent
    4. TTS: Generate response speech
    """
    try:
        # Read audio file
        audio_data = await audio_file.read()
        logger.info(f"Processing audio file: {audio_file.filename}")
        
        # Step 1: Speech-to-Text
        stt_result = None
        if "stt" in modules:
            stt_module = modules["stt"]
            stt_result = stt_module.transcribe(audio_data, language=language)
            logger.info(f"STT result: {stt_result}")
        else:
            return {"error": "STT module not available", "success": False}
        
        if not stt_result.get("success", False):
            return {"error": "STT failed", "stt_result": stt_result, "success": False}
        
        text = stt_result.get("text", "")
        
        # Step 2: Intent Recognition
        intent_result = None
        if "intent" in modules:
            intent_module = modules["intent"]
            intent_result = intent_module.recognize_intent(text)
            logger.info(f"Intent result: {intent_result}")
        else:
            return {"error": "Intent module not available", "success": False}
        
        if not intent_result.get("success", False):
            return {"error": "Intent recognition failed", "intent_result": intent_result, "success": False}
        
        intent = intent_result.get("intent", "")
        entities = intent_result.get("entities", {})
        
        # Step 3: Action Execution
        action_result = None
        if "actions" in modules:
            actions_module = modules["actions"]
            action_result = actions_module.execute_action(intent, entities)
            logger.info(f"Action result: {action_result}")
        else:
            action_result = {"success": True, "message": "No action module available"}
        
        # Step 4: Text-to-Speech for response
        tts_result = None
        response_text = action_result.get("message", f"Processed intent: {intent}")
        
        if "tts" in modules:
            tts_module = modules["tts"]
            if voice:
                tts_module.set_voice(voice)
            tts_result = tts_module.speak(response_text)
            logger.info(f"TTS result: {tts_result}")
        
        return {
            "success": True,
            "pipeline": {
                "stt": stt_result,
                "intent": intent_result,
                "action": action_result,
                "tts": tts_result
            },
            "response_text": response_text
        }
        
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process_intent")
async def process_intent(request: ProcessIntentRequest):
    """
    Process text through intent recognition and action execution.
    """
    try:
        text = request.text
        context = request.context or {}
        
        logger.info(f"Processing intent for text: '{text}'")
        
        # Step 1: Intent Recognition
        intent_result = None
        if "intent" in modules:
            intent_module = modules["intent"]
            intent_result = intent_module.recognize_intent(text, **context)
            logger.info(f"Intent result: {intent_result}")
        else:
            return {"error": "Intent module not available", "success": False}
        
        if not intent_result.get("success", False):
            return {"error": "Intent recognition failed", "intent_result": intent_result, "success": False}
        
        intent = intent_result.get("intent", "")
        entities = intent_result.get("entities", {})
        
        # Step 2: Action Execution
        action_result = None
        if "actions" in modules:
            actions_module = modules["actions"]
            action_result = actions_module.execute_action(intent, entities, **context)
            logger.info(f"Action result: {action_result}")
        else:
            action_result = {"success": True, "message": "No action module available"}
        
        return {
            "success": True,
            "intent": intent_result,
            "action": action_result,
            "response_text": action_result.get("message", f"Processed intent: {intent}")
        }
        
    except Exception as e:
        logger.error(f"Error processing intent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/speak")
async def speak_text(request: ProcessAudioRequest):
    """
    Convert text to speech using the configured TTS module.
    """
    try:
        if not request.text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        if "tts" not in modules:
            raise HTTPException(status_code=503, detail="TTS module not available")
        
        tts_module = modules["tts"]
        
        # Set voice if provided
        if request.voice:
            tts_module.set_voice(request.voice)
        
        result = tts_module.speak(request.text)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in text-to-speech: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/transcribe")
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    language: str = Form("en")
):
    """
    Transcribe audio to text using the configured STT module.
    """
    try:
        if "stt" not in modules:
            raise HTTPException(status_code=503, detail="STT module not available")
        
        audio_data = await audio_file.read()
        stt_module = modules["stt"]
        
        result = stt_module.transcribe(audio_data, language=language)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in speech-to-text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/modules/reload")
async def reload_modules():
    """Reload all modules from configuration."""
    try:
        global modules
        modules = module_loader.reload_all_modules()
        
        # Re-initialize modules
        for module_name, module in modules.items():
            if hasattr(module, 'initialize'):
                module.initialize()
        
        return {"success": True, "message": "Modules reloaded successfully"}
        
    except Exception as e:
        logger.error(f"Error reloading modules: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

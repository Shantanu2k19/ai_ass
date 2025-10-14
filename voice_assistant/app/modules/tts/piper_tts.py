"""
Piper Text-to-Speech implementation.
Efficient implementation that loads the model once and reuses it.
"""

import os
import tempfile
from typing import Dict, Any, Optional
from .base import BaseTTS
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from constants import PIPER_MODELS

try:
    from piper import PiperVoice
    PIPER_AVAILABLE = True
except ImportError:
    PIPER_AVAILABLE = False
    PiperVoice = None


class PiperTTS(BaseTTS):
    """Piper Text-to-Speech implementation with efficient model loading."""
    
    def __init__(self, model_path: Optional[str] = None):
        super().__init__()
        # Use constants for default configuration
        self.base_path = PIPER_MODELS["base_path"]
        self.voice_models = PIPER_MODELS["models"]
        self.default_voice = PIPER_MODELS["default_voice"]
        
        # Set model path - if provided, use it; otherwise use default from constants
        if model_path:
            self.model_path = model_path
        else:
            default_model_file = self.voice_models[self.default_voice]
            self.model_path = os.path.join(self.base_path, default_model_file)
        
        self.voice = None
        self.current_voice = self.default_voice
        self.available_voices = list(self.voice_models.keys())
        self._model_loaded = False
    
    def initialize(self) -> bool:
        """Initialize Piper TTS engine and load the model."""
        if not PIPER_AVAILABLE:
            self.logger.error("Piper TTS not available. Please install: pip install piper-tts")
            return False
            
        try:
            self.logger.info(f"Initializing Piper TTS with model: {self.model_path}")
            
            # Check if model file exists
            if not os.path.exists(self.model_path):
                self.logger.error(f"Model file not found: {self.model_path}")
                return False
            
            # Load the model once
            self.voice = PiperVoice.load(self.model_path)
            self._model_loaded = True
            self.is_initialized = True
            
            self.logger.info("Piper TTS initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Piper TTS: {str(e)}")
            return False
    
    def speak(self, text: str, **kwargs) -> Dict[str, Any]:
        """Convert text to speech using Piper TTS."""
        if not self.is_initialized or not self._model_loaded:
            return {"error": "Piper TTS not initialized", "success": False}
        
        try:
            self.logger.info(f"Piper TTS speaking: '{text}'")
            
            # Generate audio chunks
            audio_chunks = self.voice.synthesize(text)
            
            # Convert to list to avoid consuming the iterator twice
            chunks_list = list(audio_chunks)
            
            if not chunks_list:
                return {"error": "No audio chunks generated", "success": False}
            
            # Combine all chunks into raw PCM bytes
            wav_bytes = b"".join(chunk.audio_int16_bytes for chunk in chunks_list)
            
            # Get audio properties from the first chunk
            first_chunk = chunks_list[0]
            sample_rate = first_chunk.sample_rate
            sample_channels = first_chunk.sample_channels
            sample_width = first_chunk.sample_width
            
            # Create temporary file for audio output
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                # Write WAV header and audio data
                self._write_wav_file(temp_file, wav_bytes, sample_rate, sample_channels, sample_width)
                audio_file_path = temp_file.name
            
            # Calculate duration (approximate)
            duration = len(wav_bytes) / (sample_rate * sample_channels * sample_width)
            
            self.logger.info(f"Audio generated: {sample_rate}Hz, {sample_channels} channel(s), {duration:.2f}s")
            
            return {
                "success": True,
                "text": text,
                "voice": self.current_voice,
                "audio_file": audio_file_path,
                "audio_data": wav_bytes,
                "sample_rate": sample_rate,
                "sample_channels": sample_channels,
                "sample_width": sample_width,
                "duration": duration,
                "quality": "high"
            }
            
        except Exception as e:
            self.logger.error(f"Piper TTS error: {str(e)}")
            return {"error": str(e), "success": False}
    
    def _write_wav_file(self, file, audio_data: bytes, sample_rate: int, channels: int, sample_width: int):
        """Write WAV file header and audio data."""
        import wave
        import struct
        
        # WAV file header
        file.write(b'RIFF')
        file.write(struct.pack('<I', 36 + len(audio_data)))
        file.write(b'WAVE')
        file.write(b'fmt ')
        file.write(struct.pack('<I', 16))  # fmt chunk size
        file.write(struct.pack('<H', 1))   # audio format (PCM)
        file.write(struct.pack('<H', channels))
        file.write(struct.pack('<I', sample_rate))
        file.write(struct.pack('<I', sample_rate * channels * sample_width))
        file.write(struct.pack('<H', channels * sample_width))
        file.write(struct.pack('<H', sample_width * 8))
        file.write(b'data')
        file.write(struct.pack('<I', len(audio_data)))
        file.write(audio_data)
    
    def get_available_voices(self) -> list:
        """Get list of available voices."""
        return self.available_voices.copy()
    
    def set_voice(self, voice: str) -> bool:
        """Set the voice to use for speech synthesis."""
        if voice not in self.available_voices:
            self.logger.warning(f"Voice '{voice}' not available. Available voices: {self.available_voices}")
            return False
        
        # If changing voice, we need to reload the model
        if voice != self.current_voice:
            self.current_voice = voice
            # Get model file from constants
            new_model_file = self.voice_models.get(voice)
            if new_model_file:
                new_model_path = os.path.join(self.base_path, new_model_file)
                if new_model_path != self.model_path:
                    self.model_path = new_model_path
                    # Reinitialize with new model
                    return self.initialize()
        
        return True
    
    def cleanup(self):
        """Clean up resources."""
        if self.voice:
            # Piper doesn't have explicit cleanup, but we can reset state
            self.voice = None
            self._model_loaded = False
            self.is_initialized = False
            self.logger.info("Piper TTS cleaned up")
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the TTS module."""
        status = super().get_status()
        status.update({
            "model_loaded": self._model_loaded,
            "model_path": self.model_path,
            "piper_available": PIPER_AVAILABLE
        })
        return status

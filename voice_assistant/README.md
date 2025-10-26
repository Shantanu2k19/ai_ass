# Voice Assistant Platform - Project Summary

## Project Overview

This is a complete modular voice assistant platform built with FastAPI that can run on Raspberry Pi or cloud infrastructure. The platform features a pluggable architecture where each component (TTS, STT, Intent Recognition, Actions) can be easily swapped and extended.

## Project Structure

```
voice_assistant/
├── app/
│   ├── core/
│   │   ├── config.py          # Configuration management
│   │   └── module_loader.py   # Dynamic module loading
│   ├── modules/
│   │   ├── tts/               # Text-to-Speech modules, using piper by default 
│   │   │   ├── base.py
│   │   │   ├── google_tts.py
│   │   │   └── elevenlabs_tts.py
│   │   ├── stt/               # Speech-to-Text modules
│   │   │   ├── base.py
│   │   │   ├── whisper_stt.py
│   │   │   └── vosk_stt.py
│   │   ├── intent/            # Intent Recognition modules
│   │   │   ├── base.py
│   │   │   ├── rasa_intent.py
│   │   │   └── llm_intent.py
│   │   └── actions/           # Action modules
│   │       ├── base.py
│   │       └── light_control.py
│   └── main.py                # FastAPI application
├── config.yaml               # Module configuration
├── requirements.txt          # Python dependencies
├── setup.sh                 # Setup script
├── start.sh                 # Startup script
├── run_server.py            # Server runner
├── test_setup.py            # Setup verification
├── example_client.py        # API testing client
└── README.md                # Documentation
```

## Key Features

### Completed Features

1. **Modular Architecture**: Each component is a separate module with a common interface
2. **Dynamic Module Loading**: Modules are loaded at runtime based on configuration
3. **FastAPI Server**: RESTful API with automatic documentation
4. **Multiple Module Implementations**:
   - TTS: Piper
   - STT: Whisper STT, Vosk STT
   - Intent: Rasa Intent, LLM Intent(chatgpt and gemini)
   - Actions: Light Control
5. **Configuration Management**: YAML-based configuration system

### Module System

Each module follows the same pattern:
1. **Base Class**: Abstract base class defining the interface
2. **Concrete Implementation**: Specific implementation of the module
3. **Configuration**: Module selection via `config.yaml`
4. **Dynamic Loading**: Automatic loading and initialization

## Usage Examples

### Basic Setup
```bash
# Quick setup
./setup.sh

# Start server
./start.sh
```

### Switching Modules
```yaml
# config.yaml
tts: "tts.elevenlabs_tts.ElevenLabsTTS"
stt: "stt.vosk_stt.VoskSTT"
intent: "intent.rasa_intent.RasaIntent"
```





#### todo:
1. add scheduler using threading, and improve rasa model to also give eta 
modes in ai talkback
2. TheHood mode in llm intent, use different api for llm 
3. conversation lock, continue conversation

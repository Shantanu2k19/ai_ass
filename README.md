## Project Overview

This is a complete modular voice assistant platform built with FastAPI designed to run on Raspberry Pi or cloud infrastructure. The platform features a pluggable architecture where each component (TTS, STT, Intent Recognition, Actions) can be easily swapped and extended without code modifications.

### Architecture Philosophy

The system is designed with **modularity** and **extensibility** as core principles:
- **Hot-swappable modules**: Switch between different implementations via configuration
- **Unified interfaces**: All modules follow a common base interface
- **RESTful API**: Easy integration with web dashboards and IoT devices
- **Resource-aware**: Modules optimized for both high-performance and edge computing



## Project Structure

```
ai_ass/                          # Root project directory
│
├── voice_assistant/             # Main Voice Assistant Application (FastAPI)
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py          # Central configuration management
│   │   │   └── module_loader.py   # Dynamic module loading system
│   │   ├── modules/               # Modular component implementations
│   │   │   ├── tts/               # Text-to-Speech engines
│   │   │   │   ├── base.py        # Base TTS interface
│   │   │   │   ├── piper_tts.py   # Piper TTS (default, offline)
│   │   │   │   ├── google_tts.py  # Google Cloud TTS
│   │   │   │   └── elevenlabs_tts.py # ElevenLabs TTS
│   │   │   ├── stt/               # Speech-to-Text engines
│   │   │   │   ├── base.py        # Base STT interface
│   │   │   │   ├── whisper_stt.py # OpenAI Whisper (high accuracy)
│   │   │   │   └── vosk_stt.py    # Vosk STT (lightweight, offline)
│   │   │   ├── intent/            # Intent Recognition engines
│   │   │   │   ├── base.py        # Base intent interface
│   │   │   │   ├── rasa_intent.py # Rasa NLU integration
│   │   │   │   └── llm_intent.py  # LLM-based intent (GPT/Gemini)
│   │   │   └── actions/           # Action execution modules
│   │   │       ├── base.py        # Base action interface
│   │   │       └── light_control.py # Smart light control
│   │   ├── main.py                # FastAPI application entry point
│   │   ├── constants.py           # Application constants
│   │   └── __init__.py
│   ├── config.yaml                # Module configuration (select active modules)
│   ├── requirements.txt           # Python dependencies
│   ├── setup.sh                   # Environment setup script
│   ├── start.sh                   # Server startup script
│   ├── run_server.py              # Server runner
│   ├── test_setup.py              # Installation verification tests
│   ├── example_client.py          # Example API usage client
│   └── README.md                  # Detailed documentation
│
├── m_app/                         # Web Dashboard (Flask)
│   ├── app.py                     # Flask application
│   ├── requirements.txt           # Flask dependencies
│   └── templates/
│       ├── login.html             # Login page
│       └── dashboard.html          # Control dashboard
│
├── rasa_nlu/                      # Rasa Training Project
│   ├── config.yml                 # Rasa configuration
│   ├── data/
│   │   └── nlu.yml                # Training data
│   ├── domain.yml                 # Domain definition
│   └── models/                    # Trained models
│
├── exp_files/                     # Experimental & Testing Files
│   ├── vosk-model-small-en-in-0.4/ # Vosk model files
│   ├── model/                     # Additional ASR models
│   ├── en_US-*.onnx              # Piper TTS voice models
│   ├── *.py                       # Individual module tests
│   └── __pycache__/
│
└── nodeMcu/                       # ESP8266/NodeMCU Firmware
    ├── arduino_file.ino           # IoT device firmware
    └── commandsMQT.txt             # MQTT command reference
```

## Key Features

### Completed Features

1. **Modular Architecture**: Each component is a separate module with a common interface
2. **Dynamic Module Loading**: Modules are loaded at runtime based on configuration
3. **FastAPI Server**: RESTful API with automatic OpenAPI documentation
4. **Web Dashboard**: Flask-based control panel for remote management
5. **Multiple Module Implementations**:
   - **TTS Modules**: Piper (offline, fast), Google Cloud TTS, ElevenLabs
   - **STT Modules**: Whisper (high accuracy), Vosk (lightweight, offline)
   - **Intent Modules**: Rasa NLU (rule-based), LLM-based (GPT-4, Gemini)
   - **Action Modules**: Smart light control (extensible for more IoT devices)
6. **Configuration Management**: YAML-based configuration system
7. **IoT Integration**: NodeMCU/ESP8266 firmware for hardware control

### Module System

Each module follows a consistent pattern for easy extension:

1. **Base Class** (`base.py`): Abstract base class defining the common interface
2. **Concrete Implementation**: Specific implementation with optimized logic
3. **Configuration** (`config.yaml`): Select which module to use at runtime
4. **Dynamic Loading**: Automatic discovery and initialization without code changes

### Module Types

- **TTS (Text-to-Speech)**: Convert text to natural-sounding speech audio
- **STT (Speech-to-Text)**: Transcribe audio to text with high accuracy
- **Intent Recognition**: Understand user intent and extract entities
- **Actions**: Execute commands and control IoT devices

## Component Overview

### Voice Assistant (`voice_assistant/`)
The core FastAPI application that handles:
- Speech processing pipeline (STT → Intent → Actions → TTS)
- RESTful API for voice interactions
- Dynamic module loading based on `config.yaml`
- Support for multiple TTS, STT, and Intent engines

### Web Dashboard (`m_app/`)
Flask-based web application for:
- Remote control and monitoring
- User authentication and access management
- Real-time status updates
- Module configuration management

### Rasa NLU (`rasa_nlu/`)
Training environment for the Rasa natural language understanding model:
- Intent classification training data
- Entity extraction configuration
- Model version management

### Experimental Files (`exp_files/`)
Development and testing workspace containing:
- Individual module test scripts
- Model files (Vosk, Piper voices)
- Quick validation scripts

### IoT Firmware (`nodeMcu/`)
Arduino-based firmware for ESP8266/NodeMCU devices:
- MQTT communication for smart device control
- Home automation integration









### Upcoming Features

- **Task Scheduler**: Implement threading-based scheduling for recurring tasks
- **Enhanced Rasa Model**: Add ETA estimation and AI talkback modes
- **TheHood Mode**: support for casual mode to talk to assitant with different tone
- **Conversation Management**: Implement conversation locks and context continuation


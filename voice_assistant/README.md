quici commands : 
running server :

uvicorn app.main:app --reload


## Project Structure

```
voice_assistant/
├── app/
│   ├── core/
│   │   ├── config.py          # Configuration management
│   │   └── module_loader.py   # Dynamic module loading
│   ├── modules/
│   │   ├── tts/
│   │   │   ├── base.py
│   │   │   ├── google_tts.py
│   │   │   └── elevenlabs_tts.py
│   │   ├── stt/
│   │   │   ├── base.py
│   │   │   ├── whisper_stt.py
│   │   │   └── vosk_stt.py
│   │   ├── intent/
│   │   │   ├── base.py
│   │   │   ├── rasa_intent.py
│   │   │   └── llm_intent.py
│   │   └── actions/
│   │       ├── base.py
│   │       └── light_control.py
│   └── main.py                # FastAPI application
├── config.yaml               # Module configuration
├── requirements.txt          # Python dependencies
└── README.md
```

## Quick Start
chmod +x setup.sh
./setup.sh

#### Manual Setup
pip install -r requirements.txt

### Configuration

`config.yaml` to specify which modules to use:

```yaml
# Text-to-Speech module
tts: "tts.google_tts.GoogleTTS"

# Speech-to-Text module  
stt: "stt.whisper_stt.WhisperSTT"

# Intent Recognition module
intent: "intent.llm_intent.LLMIntent"

# Actions module
actions: "actions.light_control.LightControl"
```

### Run the Server

#### Option A: Using the startup script (Recommended)
./start.sh


#### Option B: Manual startup
python run_server.py

# Or using the original method
python -m app.main


The server will be available at `http://localhost:8000`

### 4. Test the API

Visit `http://localhost:8000/docs` for the interactive API documentation.

## API Endpoints

### Health Check
```bash
GET /health
```

### Process Audio (Complete Pipeline)
```bash
POST /process_audio
Content-Type: multipart/form-data

# Form data:
# - audio_file: Audio file (WAV, MP3, etc.)
# - language: Language code (default: "en")
# - voice: Voice name (optional)
```

### Process Intent (Text Input)
```bash
POST /process_intent
Content-Type: application/json

{
  "text": "Turn on the lights",
  "context": {}
}
```

### Text-to-Speech
```bash
POST /speak
Content-Type: application/json

{
  "text": "Hello, how can I help you?",
  "voice": "en-US-Standard-A"
}
```

### Speech-to-Text
```bash
POST /transcribe
Content-Type: multipart/form-data

# Form data:
# - audio_file: Audio file
# - language: Language code
```

### Module Management
```bash
# Get module status
GET /modules/status

# Reload modules
POST /modules/reload
```

## 🔄 Example Flow

1. **Wake Word Detection** (external script):
   ```python
   # External wake word listener detects "Hey Pi"
   # Records audio and sends to FastAPI
   ```

2. **Audio Processing**:
   ```bash
   curl -X POST "http://localhost:8000/process_audio" \
        -F "audio_file=@audio.wav" \
        -F "language=en"
   ```

3. **Pipeline Execution**:
   - STT converts audio to text
   - Intent module identifies user intent
   - Action module executes the command
   - TTS generates response speech

## 🧩 Adding New Modules

### 1. Create Module Implementation

Create a new file in the appropriate module directory:

```python
# app/modules/tts/my_tts.py
from .base import BaseTTS

class MyTTS(BaseTTS):
    def initialize(self) -> bool:
        # Initialize your TTS engine
        return True
    
    def speak(self, text: str, **kwargs) -> Dict[str, Any]:
        # Implement text-to-speech
        return {"success": True, "audio_file": "output.wav"}
    
    def get_available_voices(self) -> list:
        # Return available voices
        return ["voice1", "voice2"]
```

### 2. Update Configuration

Add your module to `config.yaml`:

```yaml
tts: "tts.my_tts.MyTTS"
```

### 3. Restart Server

The server will automatically load your new module on startup.

## 🔧 Module Configuration

### Switching Between Modules

To switch between different implementations, simply update `config.yaml`:

```yaml
# Use ElevenLabs instead of Google TTS
tts: "tts.elevenlabs_tts.ElevenLabsTTS"

# Use Vosk instead of Whisper STT
stt: "stt.vosk_stt.VoskSTT"

# Use Rasa instead of LLM Intent
intent: "intent.rasa_intent.RasaIntent"
```

### Module-Specific Settings

You can add module-specific settings to `config.yaml`:

```yaml
tts: "tts.google_tts.GoogleTTS"
tts_settings:
  api_key: "your-api-key"
  default_voice: "en-US-Standard-A"

stt: "stt.whisper_stt.WhisperSTT"
stt_settings:
  model_size: "base"
  language: "en"
```

## 🐳 Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t voice-assistant .
docker run -p 8000:8000 voice-assistant
```

## 🍓 Raspberry Pi Setup

### 1. Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip -y

# Install audio dependencies
sudo apt install portaudio19-dev python3-pyaudio -y

# Install project dependencies
pip3 install -r requirements.txt
```

### 2. Configure Audio

```bash
# Test audio input/output
arecord -l  # List input devices
aplay -l   # List output devices
```

### 3. Run as Service

Create `/etc/systemd/system/voice-assistant.service`:

```ini
[Unit]
Description=Voice Assistant Platform
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/voice_assistant
ExecStart=/usr/bin/python3 -m app.main
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable voice-assistant
sudo systemctl start voice-assistant
```

## 🔌 MQTT Integration (Optional)

The platform supports MQTT for inter-module communication. Enable in `config.yaml`:

```yaml
settings:
  mqtt:
    enabled: true
    broker: "localhost"
    port: 1883
    username: "mqtt_user"
    password: "mqtt_pass"
```

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

## 📝 Development

### Code Style

The project uses Black for code formatting and Flake8 for linting:

```bash
# Format code
black app/

# Lint code
flake8 app/
```

### Adding New Features

1. Create feature branch
2. Implement changes
3. Add tests
4. Update documentation
5. Submit pull request

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue on GitHub
- Check the documentation
- Review the API docs at `/docs`

## 🔮 Future Enhancements

- [ ] Real-time audio streaming
- [ ] Wake word detection module
- [ ] Home Assistant integration
- [ ] Cloud deployment templates
- [ ] Mobile app companion
- [ ] Voice cloning capabilities
- [ ] Multi-language support
- [ ] Conversation memory
- [ ] Plugin marketplace

---

**Happy Voice Assisting! 🎤🤖**





#### todo:
add scheduler using hreading, and improve rasa model to also give eta 
modes in ai talkback, TheHood mode, use different api for llm 
conversation lock, continue conversation

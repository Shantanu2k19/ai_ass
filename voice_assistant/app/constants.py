INTENT_CONFIDENCE_THRESHOLD = 0.6

MQTT_BROKER = "localhost"
TOPIC = "home/livingroom/light"

# Model paths
RASA_MODEL_PATH = "app/modules/intent/rasa_models/nlu-20251012-114449-snowy-dimension.tar.gz"

# TTS model paths
PIPER_MODELS = {
    "base_path": "app/modules/tts/models",
    "models": {
        "lessac_medium": "en_US-lessac-medium.onnx",
        "amy_medium": "en_US-amy-medium.onnx", 
        "ryan_high": "en_US-ryan-high.onnx"
    },
    "default_voice": "lessac_medium"
}
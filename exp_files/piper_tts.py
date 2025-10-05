import wave
from piper import PiperVoice

voice = PiperVoice.load("en_US-lessac-medium.onnx")
with wave.open("test.wav", "wb") as wav_file:
    voice.synthesize_wav("Welcome to the world of speech synthesis!", wav_file)

# https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/API_PYTHON.md

#https://rhasspy.github.io/piper-samples/#en_US-bryce-medium
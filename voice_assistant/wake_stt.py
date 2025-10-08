import os
import sys
import struct
import queue
import pyaudio
import pvporcupine
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from dotenv import load_dotenv
import json
import time

load_dotenv()

# ---------- VARS ----------

wake_word = 'alexa'
MODEL_PATH = "vosk-model-small-en-in-0.4"
max_record_len = 6 #seconds

# ------------------- PORCUPINE SETUP -------------------
porc_access_key = os.environ.get('porc_env_key')
if not porc_access_key:
    print("Porcupine access key not found in .env!")
    exit(1)

# Initialize wake word detector (e.g., "alexa")
porcupine = pvporcupine.create(
    access_key=porc_access_key,
    keywords=[wake_word]
)

pa = pyaudio.PyAudio()
audio_stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)

print("Wake word detection initialized.")
print("Listening for wake word...")

# ------------------- VOSK SETUP -------------------
if not os.path.exists(MODEL_PATH):
    print(f"Vosk model not found at {MODEL_PATH}")
    exit(1)

vosk_model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(vosk_model, 16000)

# ------------------- FUNCTIONS -------------------
def listen_and_transcribe():
    """
    Records voice after wake word detection until silence and returns recognized text.
    """
    print("listening...")
    q = queue.Queue()
    stop_time = time.time() + max_record_len
    def callback(indata, frames, time_info, status):
        if status:
            print(status, file=sys.stderr)
        q.put(bytes(indata))

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        result_text = ""
        while time.time() < stop_time:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                if "text" in result and result["text"]:
                    result_text += " " + result["text"]
            else:
                partial = json.loads(recognizer.PartialResult()).get("partial", "")
        # Finalize
        final_result = json.loads(recognizer.FinalResult()).get("text", "")
        result_text += " " + final_result
    return result_text.strip()


# ------------------- MAIN LOOP -------------------
try:
    while True:
        pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

        result = porcupine.process(pcm)
        if result >= 0:
            print("\n Wake word detected!")
            text = listen_and_transcribe()
            if text:
                print(f" You said: {text}")
            else:
                print(" No speech detected.")
            print("\n Listening for wake word again...")

except KeyboardInterrupt:
    print(" Stopping gracefully...")
finally:
    if audio_stream:
        audio_stream.stop_stream()
        audio_stream.close()
    pa.terminate()
    porcupine.delete()

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
SILENCE_LIMIT = 0.5
MAX_LISTEN_TIME = 7

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

# ------------------- VOSK SETUP -------------------
if not os.path.exists(MODEL_PATH):
    print(f"Vosk model not found at {MODEL_PATH}")
    exit(1)

vosk_model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(vosk_model, 16000)

# ------------------- FUNCTIONS -------------------
def listen_and_transcribe(silence_limit=SILENCE_LIMIT, max_listen_time=MAX_LISTEN_TIME):
    """
    Records voice until silence is detected or max time reached.
    Returns recognized text.
    """
    print("\nListening...")
    q = queue.Queue()
    speaking = False
    result_text = ""
    start_time = time.time()
    last_speech_time = start_time

    def callback(indata, frames, time_info, status):
        if status:
            print(f"[WARN] Audio input status: {status}", file=sys.stderr)
        q.put(bytes(indata))

    try:
        with sd.RawInputStream(
            samplerate=16000, blocksize=8000, dtype='int16',
            channels=1, callback=callback
        ):
            recognizer.Reset()
            print("[INFO] Waiting for voice input...")

            while True:
                if (time.time() - start_time) > max_listen_time:
                    print("[WARN] Max listen time reached. Stopping...")
                    break

                try:
                    data = q.get(timeout=1)
                except queue.Empty:
                    continue

                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    if "text" in result and result["text"]:
                        speaking = True
                        last_speech_time = time.time()
                        result_text += " " + result["text"]
                        print(f"[SPEECH] Segment: {result['text']}")
                    else:
                        print(f"[DEBUG] Empty result: {result}")
                else:
                    partial = json.loads(recognizer.PartialResult()).get("partial", "")
                    if partial:
                        speaking = True
                        last_speech_time = time.time()
                        # print(f"[PARTIAL] {partial}")

                if speaking and (time.time() - last_speech_time) > silence_limit:
                    print("[INFO] Silence detected. Ending recording.")
                    break

        # finalize result
        final_result = json.loads(recognizer.FinalResult()).get("text", "")
        result_text += " " + final_result
        result_text = result_text.strip()

        if result_text:
            print(f"[RESULT] You said: '{result_text}'")
        else:
            print("[RESULT] No clear speech detected.")

        return result_text

    except Exception as e:
        print(f"[ERROR] Error during transcription: {e}")
        return ""

# ------------------- MAIN LOOP -------------------
try:
    print("\n\nWake word detection initialized.")
    print("Listening for wake word...")
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

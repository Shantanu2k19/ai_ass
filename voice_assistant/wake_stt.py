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
NO_SPEECH_TIMEOUT = 2
MAX_SPEECH_LIMIT = 12

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
def listen_and_transcribe(
    silence_limit=SILENCE_LIMIT,
    no_speech_timeout=NO_SPEECH_TIMEOUT,         
    long_speech_timeout=MAX_SPEECH_LIMIT
):
    """
    Records voice until silence is detected, no-speech timeout, or long-speech timeout.
    Returns recognized text.
    """
    print("\nListening...")
    q = queue.Queue()
    speaking = False
    result_text = ""
    start_time = time.time()          # when listening started
    first_speech_time = None          # when speech starts
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
                # --- CASE 1: User says wake word but stays silent ---
                if not speaking and (time.time() - start_time) > no_speech_timeout:
                    print("[WARN] No speech detected after wake word. Timing out...")
                    break

                try:
                    data = q.get(timeout=1)
                except queue.Empty:
                    continue

                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    if "text" in result and result["text"]:
                        if not speaking:
                            speaking = True
                            first_speech_time = time.time()
                        last_speech_time = time.time()
                        result_text += " " + result["text"]
                        # print(f"[SPEECH] Segment: {result['text']}")
                    else:
                        print(f"[DEBUG] Empty result: {result}")
                else:
                    partial = json.loads(recognizer.PartialResult()).get("partial", "")
                    if partial:
                        if not speaking:
                            speaking = True
                            first_speech_time = time.time()
                        last_speech_time = time.time()
                        # print(f"[PARTIAL] {partial}")

                # --- CASE 2: Continuous long talking ---
                if speaking and first_speech_time:
                    if (time.time() - first_speech_time) > long_speech_timeout:
                        print("[WARN] Long speech timeout reached. Stopping...")
                        break

                # --- CASE 3: Silence detected ---
                if speaking and (time.time() - last_speech_time) > silence_limit:
                    print("[INFO] Silence detected. Ending recording.")
                    break

        # --- Finalize transcription ---
        final_result = json.loads(recognizer.FinalResult()).get("text", "")
        result_text += " " + final_result
        result_text = result_text.strip()

        if result_text:
            print(f"[RESULT] '{result_text}'")
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

import os
import sys
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer

# Load model
# model = Model("model_heavy")
model = Model("model")
recognizer = KaldiRecognizer(model, 16000)

# Audio input queue
q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

# Open microphone stream
with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                       channels=1, callback=callback):
    print("🎤 Listening... (Ctrl+C to stop)")
    while True:
        data = q.get()
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            print(result)
        else:
            partial = recognizer.PartialResult()
            print(partial)

# https://alphacephei.com/vosk/models
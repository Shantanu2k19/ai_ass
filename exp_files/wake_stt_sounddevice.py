import pvporcupine 
import sounddevice as sd
import numpy as np
import os 

porc_access_key = "KdHBf5fY1ODcyh+DmICcPnkeTqpcOkSophtco6GTSP6mxI+oaAISdw==" #os.environ.get('porc_access_key', None)
if not porc_access_key:
    print('Porcupine access key not found!')
    exit(1)

porcupine = pvporcupine.create(
    access_key=porc_access_key, 
    keywords=['alexa']
)

# porcupine = pvporcupine.create(
#     access_key=porc_access_key, 
#     keyword_paths=['/home/Downloads/zodiac_en_raspberry-pi_v3_0_0/zodiac_en_raspberry-pi_v3_0_0.ppn']
# )

print("Listening for wake word...")

def audio_callback(indata, frames, time, status):
    if status:
        print(f"Audio callback status: {status}")
    
    # Convert float32 to int16 (PyAudio format)
    audio_data = (indata * 32767).astype(np.int16).flatten()
    
    # Process with Porcupine
    result = porcupine.process(audio_data)
    if result >= 0:
        print("Wake word detected!")

try:
    # Open audio stream with sounddevice
    with sd.InputStream(
        samplerate=porcupine.sample_rate,
        channels=1,
        dtype=np.float32,
        blocksize=porcupine.frame_length,
        callback=audio_callback
    ):
        print("Press Ctrl+C to stop...")
        while True:
            sd.sleep(100)  # Keep the stream alive
            
except KeyboardInterrupt:
    print("Stopping...")
finally:
    porcupine.delete()


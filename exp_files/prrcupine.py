import pvporcupine 
import pyaudio 
import struct 

porc_access_key = ""

porcupine = pvporcupine.create(
    access_key=porc_access_key, 
    keywords=['alexa']
)

# porcupine = pvporcupine.create(
#     access_key=porc_access_key, 
#     keyword_paths=['/home/Downloads/zodiac_en_raspberry-pi_v3_0_0/zodiac_en_raspberry-pi_v3_0_0.ppn']
# )

pa = pyaudio.PyAudio()
audio_stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)


print("Listening for wake word...")

try:
    while True:
        pcm = audio_stream.read(porcupine.frame_length)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

        result = porcupine.process(pcm)
        if result >= 0:
            print("Wake word detected!")
except KeyboardInterrupt:
    print("Stopping...")
finally:
    audio_stream.stop_stream()
    audio_stream.close()
    pa.terminate()
    porcupine.delete()
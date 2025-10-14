from piper import PiperVoice
import simpleaudio as sa
import sys

def text_to_speech(text, model_path="en_US-lessac-medium.onnx"):
    """
    Convert text to speech using Piper TTS and play it.
    
    Args:
        text (str): Text to convert to speech
        model_path (str): Path to the Piper model file
    """
    try:
        # Load model
        print(f"Loading Piper model: {model_path}")
        voice = PiperVoice.load(model_path)
        
        # Generate audio chunks
        print(f"Synthesizing: '{text}'")
        audio_chunks = voice.synthesize(text)
        
        # Convert to list to avoid consuming the iterator twice
        chunks_list = list(audio_chunks)
        
        if not chunks_list:
            print("No audio chunks generated!")
            return
        
        # Combine all chunks into raw PCM bytes
        wav_bytes = b"".join(chunk.audio_int16_bytes for chunk in chunks_list)
        
        # Play the audio using simpleaudio
        # Get audio properties from the first chunk
        first_chunk = chunks_list[0]
        print(f"Playing audio: {first_chunk.sample_rate}Hz, {first_chunk.sample_channels} channel(s)")
        
        play_obj = sa.play_buffer(
            wav_bytes,
            num_channels=first_chunk.sample_channels,
            bytes_per_sample=first_chunk.sample_width,
            sample_rate=first_chunk.sample_rate
        )
        play_obj.wait_done()
        print("Audio playback completed!")
        
    except FileNotFoundError as e:
        print(f"Error: Model file not found: {e}")
        print("Make sure the model file exists in the current directory.")
    except Exception as e:
        print(f"Error during text-to-speech conversion: {e}")

if __name__ == "__main__":
    # Default text to speak

    text = "Hi there. How are you?"
    
    # Allow custom text via command line argument
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    
    text_to_speech(text)



#CODE for vtext to audio file 
# import wave
# from piper import PiperVoice

# try:
#     voice = PiperVoice.load("en_US-lessac-medium.onnx")
#     with wave.open("test.wav", "wb") as wav_file:
#         voice.synthesize_wav("lights are turned on", wav_file)
# except Exception as e:
#     print(f"Error: {e}")
# # https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/API_PYTHON.md

# #https://rhasspy.github.io/piper-samples/#en_US-bryce-medium
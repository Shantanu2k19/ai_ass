#for microphone access
sudo apt install portaudio19-dev

#wake word
pip install pvporcupine pyaudio

#verify mics
arecord -l

#vosk
sudo apt install portaudio19-dev ffmpeg
pip install vosk sounddevice


#piper 
sudo apt install sox

pip install piper-tts



####
exp 
pip install rasa



###
other 
sudo apt install build-essential python3-dev -y
pip install paho-mqtt



rasa train
rasa run actions &
rasa shell



##TODO : add memory and continuous conversation
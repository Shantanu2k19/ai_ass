use python 3.9
pip instal rasa 
python -c "import rasa; print(rasa.__version__)"

rasa train nlu
rasa shell nlu

after training, move your updated model to ai_ass/voice_assistant/app/modules/intent/rasa_models
#!/bin/bash
# Script to start the voice assistant server with the correct virtual environment

cd /Desktop/ai_ass/voice_assistant

# Activate the virtual environment
source venv_39/bin/activate

# Verify we're using the correct Python
echo "Using Python: $(which python)"
echo "Python version: $(python --version)"

# Check if Rasa is available
python -c "import rasa; print('Rasa version:', rasa.__version__)" || {
    echo "Error: Rasa not found in virtual environment!"
    exit 1
}

# Start the server
echo "Starting Voice Assistant Server..."
python run_server.py


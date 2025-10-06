#!/bin/bash
# Voice Assistant Platform Startup Script

echo "Voice Assistant Platform"
echo "=========================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
echo "Checking dependencies..."
python -c "import fastapi, uvicorn, yaml" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Dependencies not installed. Installing..."
    pip install -r requirements.txt
fi

# Run setup test
echo "Running setup test..."
python test_setup.py

if [ $? -eq 0 ]; then
    echo ""
    echo "Setup test passed! Starting server..."
    echo ""
    python run_server.py
else
    echo "Setup test failed. Please check the errors above."
    exit 1
fi


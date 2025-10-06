#!/bin/bash
# Voice Assistant Platform Setup Script

echo "Voice Assistant Platform Setup"
echo "================================="

# Check Python version
echo "Checking Python version..."
python3 --version

# Check if Python version is 3.6 or higher
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.6"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.6 or higher is required. Current version: $python_version"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Removing old one..."
    rm -rf venv
fi

python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run setup test
echo "Running setup test..."
python test_setup.py

if [ $? -eq 0 ]; then
    echo ""
    echo "Setup completed successfully!"
    echo ""
    echo "To start the server, run:"
    echo "  ./start.sh"
    echo ""
    echo "Or manually:"
    echo "  source venv/bin/activate"
    echo "  python run_server.py"
    echo ""
    echo "The server will be available at:"
    echo "  http://localhost:8000"
    echo "  http://localhost:8000/docs (API documentation)"
else
    echo "Setup failed. Please check the errors above."
    exit 1
fi


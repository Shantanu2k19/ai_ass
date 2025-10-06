#!/bin/bash
# Voice Assistant Platform Setup Script

echo "🎤 Voice Assistant Platform Setup"
echo "================================="

# Check Python version
echo "🐍 Checking Python version..."
python3 --version

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Removing old one..."
    rm -rf venv
fi

python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Run setup test
echo "🧪 Running setup test..."
python test_setup.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Setup completed successfully!"
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
    echo "❌ Setup failed. Please check the errors above."
    exit 1
fi


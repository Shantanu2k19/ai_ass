#!/bin/bash

echo "Setup starting"
echo "=============================="

python_version=$(python3.9 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.9"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Python $required_version or higher is required. Current version: $python_version"
    echo "Install: sudo apt install python3.9 python3.9-venv -y"
    exit 1
fi

echo "Python version $python_version detected"

[ -d "venv" ] && rm -rf venv
python3.9 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

python example_test_files/test_setup.py
if [ $? -eq 0 ]; then
    echo "Setup completed successfully"
    echo "To start server:"
    echo "  ./start.sh"
    echo "Or manually:"
    echo "  source venv/bin/activate && python run_server.py"
    echo "Server URLs:"
    echo "  http://localhost:8000"
    echo "  http://localhost:8000/docs"
else
    echo "Setup failed"
    exit 1
fi

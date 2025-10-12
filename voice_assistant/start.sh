#!/bin/bash

echo "AI Ass starting..."

if [ ! -d "venv_39" ]; then
    echo "Virtual environment venv_39 not found. Please run setup."
    exit 1
fi

source venv_39/bin/activate
# python test_setup.py

if [ $? -eq 0 ]; then
    python run_server.py
else
    echo "Setup test failed. Please check the errors above."
    exit 1
fi


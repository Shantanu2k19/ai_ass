#!/bin/bash

echo "AI Ass starting..."

if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run setup."
    exit 1
fi

source venv/bin/activate
# python test_setup.py

if [ $? -eq 0 ]; then
    python run_server.py
else
    echo "Setup test failed. Please check the errors above."
    exit 1
fi


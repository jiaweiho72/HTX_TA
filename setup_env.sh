#!/bin/bash

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null
then
    echo "Python3 is not installed. Please install Python3 first."
    exit 1
fi

# Create a virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "requirements.txt not found! Skipping dependency installation."
fi

echo "Setup complete. Virtual environment is ready!"
echo "To activate it, run: source venv/bin/activate"

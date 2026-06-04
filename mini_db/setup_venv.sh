#!/bin/bash
# Kahatayn NPO System - Virtual Environment Setup (Linux/Mac)
# This script creates and configures the Python virtual environment

echo ""
echo "========================================"
echo "Kahatayn System - Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment: npo_venv..."
python3 -m venv npo_venv

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

echo ""
echo "Activating virtual environment..."
source npo_venv/bin/activate

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi

# Upgrade pip
echo ""
echo "Upgrading pip, setuptools, and wheel..."
python -m pip install --upgrade pip setuptools wheel

# Install requirements
echo ""
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Virtual environment created at: npo_venv/"
echo "To activate it in the future, run:"
echo "  source npo_venv/bin/activate"
echo ""
echo "To run the application:"
echo "  python main.py"
echo ""
echo "To build the .exe:"
echo "  ./run_build.sh"
echo ""

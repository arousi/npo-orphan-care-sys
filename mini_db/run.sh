#!/bin/bash
# Kahatayn NPO System - Development Runner
# Automatically activates venv and runs the application

echo ""
echo "========================================"
echo "Kahatayn System - Development Mode"
echo "========================================"
echo ""

# Check if venv exists
if [ ! -f "npo_venv/bin/activate" ]; then
    echo "Virtual environment not found!"
    echo "Running setup_venv.sh first..."
    echo ""
    ./setup_venv.sh
fi

# Activate venv
source npo_venv/bin/activate

# Run the application
echo ""
echo "Starting Kahatayn application..."
echo ""
python main.py

# On exit
echo ""
echo "Application closed."

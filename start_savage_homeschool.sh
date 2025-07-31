#!/bin/bash

# Savage Homeschool OS Launcher for Linux/Mac

echo "========================================"
echo "   Savage Homeschool OS Launcher"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "ERROR: Python 3.8 or higher is required"
    echo "Current version: $python_version"
    exit 1
fi

echo "Python $python_version found! Starting Savage Homeschool OS..."
echo

# Make the script executable
chmod +x run.py

# Start the application
python3 run.py

echo
echo "Savage Homeschool OS has stopped." 
#!/bin/bash

# Surgical Scout - Run Script
# This script sets up the environment and runs the Surgical Scout digest system

set -e  # Exit on error

echo "=================================="
echo "Surgical Scout - Starting..."
echo "=================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install/update requirements
echo "📥 Installing requirements..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Requirements installed"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ ERROR: .env file not found!"
    echo ""
    echo "Please create a .env file with your configuration."
    echo "See setup_gmail.md for instructions."
    exit 1
fi

# Run the scout script
echo "🚀 Running Surgical Scout..."
echo ""
python scout.py

# Capture exit code
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "=================================="
    echo "✅ Surgical Scout completed successfully!"
    echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=================================="
else
    echo "=================================="
    echo "❌ Surgical Scout encountered an error"
    echo "Check surgical_scout.log for details"
    echo "=================================="
fi

# Deactivate virtual environment
deactivate

exit $EXIT_CODE

#!/bin/bash
# Marine Storm Analysis - Unix/Linux Shell Runner
# ==============================================

echo "Marine Storm Analysis System"
echo "============================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Change to root directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "Storms/.venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv "Storms/.venv"
fi

# Activate virtual environment
source "Storms/.venv/bin/activate"

# Install/upgrade requirements
echo "Installing required packages..."
pip install -r "Storms/requirements.txt" --quiet

# Run the storm analysis
echo ""
echo "Starting storm analysis..."
echo ""
python3 "Storms/run_storm_analysis.py" "$@"

echo ""
echo "Analysis complete."

deactivate

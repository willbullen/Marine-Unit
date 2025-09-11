#!/bin/bash

# ===============================================
# Consumer Data Export - Unix/Linux Script
# ===============================================
# Builds consumer-ready CSVs from QC outputs
# - Live logger only, QC-fail values removed, no indicator columns
# - One CSV per buoy per year into Consumers/Data
# Usage: chmod +x run_consumer.sh && ./run_consumer.sh

set -e

echo "Starting Consumer Data Export on Unix/Linux..."
echo "=============================================="

# Ensure python3 exists
if ! command -v python3 &> /dev/null; then
  echo "ERROR: python3 not found in PATH"
  exit 1
fi

# Create venv if missing
if [ ! -d ".venv" ]; then
  echo "Creating Python virtual environment..."
  python3 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing required packages..."
pip install -r "QC/requirements.txt"

echo "Running consumer export..."
python "Consumers/Scripts/consumer_export.py"

echo ""
echo "=================================================="
echo "Consumer export completed successfully!"
echo "Outputs in 'Consumers/Data' (one CSV per buoy-year)"
echo "=================================================="

deactivate




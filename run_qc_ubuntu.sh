#!/bin/bash

# ===============================================
# Buoy QC Processing - Ubuntu/Linux Script
# ===============================================
# This script runs the buoy QC processing in a Python virtual environment
# Generates separate CSV files and reports for each buoy-year combination
# Run from the main project directory
# 
# Usage: ./run_qc_ubuntu.sh
# Make executable with: chmod +x run_qc_ubuntu.sh

set -e  # Exit on any error

echo "Starting Buoy QC Processing on Ubuntu/Linux..."
echo "============================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3: sudo apt update && sudo apt install python3 python3-venv python3-pip"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        echo "Please ensure python3-venv is installed: sudo apt install python3-venv"
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install/update dependencies
echo "Installing required packages..."
pip install -r "QC/requirements.txt"
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

# Clear existing yearly output files to avoid confusion
echo "Cleaning previous yearly output files..."
rm -f "QC Data"/buoy_*_2023_*.*
rm -f "QC Data"/buoy_*_2024_*.*
rm -f "QC Data"/buoy_*_2025_*.*

# Run QC processing
echo ""
echo "Running QC processing..."
echo "========================"
cd "QC"
python buoy_qc_processor.py
if [ $? -ne 0 ]; then
    echo "ERROR: QC processing failed"
    cd ..
    exit 1
fi

cd ..

echo ""
echo "=================================================="
echo "QC Processing completed successfully!"
echo ""
echo "Generated files are in the 'QC Data' folder:"
echo "- QC'd CSV files for each buoy station by year"
echo "- QC reports in markdown (*.md) and PDF (*.pdf) formats"
echo "- Color-coded visualization plots (*.png) for each year"
echo ""
echo "File naming convention:"
echo "- buoy_STATION_YEAR_qcd.csv (e.g., buoy_62091_2023_qcd.csv)"
echo "- buoy_STATION_YEAR_qc_report.md"
echo "- buoy_STATION_YEAR_qc_overview.png"
echo ""
echo "Scripts preserved in 'QC Scripts' folder for future use."
echo "=================================================="

# Deactivate virtual environment
deactivate

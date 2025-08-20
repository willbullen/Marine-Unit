#!/bin/bash

# ===============================================
# Buoy QC Web Application - Ubuntu Startup
# ===============================================
# This script starts the Django backend server
# Run from the webapp directory
# 
# Usage: ./run_webapp_ubuntu.sh
# Make executable with: chmod +x run_webapp_ubuntu.sh

set -e  # Exit on any error

echo "Starting Buoy QC Web Application..."
echo "===================================="

# Activate virtual environment
echo "Activating virtual environment..."
source ../.venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    echo "Please run this from the webapp directory"
    exit 1
fi

# Install Django dependencies if needed
echo "Installing Django dependencies..."
pip install django djangorestframework django-cors-headers

# Run Django migrations
echo "Running Django migrations..."
python manage.py migrate

# Display information
echo ""
echo "===================================="
echo "Django server will start on http://127.0.0.1:8000"
echo ""
echo "Available endpoints:"
echo "- http://127.0.0.1:8000/ (Main page)"
echo "- http://127.0.0.1:8000/api/dashboard/ (Dashboard API)"
echo "- http://127.0.0.1:8000/api/stations/ (Stations API)"
echo "- http://127.0.0.1:8000/admin/ (Django Admin)"
echo ""
echo "To create an admin user, run:"
echo "python manage.py createsuperuser"
echo "===================================="
echo ""

# Start Django development server
echo "Starting Django server..."
python manage.py runserver

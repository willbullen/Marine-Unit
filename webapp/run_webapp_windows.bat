@echo off
REM ===============================================
REM Buoy QC Web Application - Windows Startup
REM ===============================================
REM This script starts the Django backend server
REM Run from the webapp directory

echo Starting Buoy QC Web Application...
echo ====================================

REM Activate virtual environment
echo Activating virtual environment...
call ..\.venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    echo Please run this from the webapp directory
    pause
    exit /b 1
)

REM Install Django dependencies if needed
echo Installing Django dependencies...
pip install django djangorestframework django-cors-headers

REM Run Django migrations
echo Running Django migrations...
python manage.py migrate

REM Create superuser prompt
echo.
echo ====================================
echo Django server will start on http://127.0.0.1:8000
echo.
echo Available endpoints:
echo - http://127.0.0.1:8000/ (Main page)
echo - http://127.0.0.1:8000/api/dashboard/ (Dashboard API)
echo - http://127.0.0.1:8000/api/stations/ (Stations API)
echo - http://127.0.0.1:8000/admin/ (Django Admin)
echo.
echo To create an admin user, run:
echo python manage.py createsuperuser
echo ====================================
echo.

REM Start Django development server
echo Starting Django server...
python manage.py runserver

pause

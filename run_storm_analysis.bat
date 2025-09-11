@echo off
REM Marine Storm Analysis - Windows Batch Runner
REM ============================================

echo Marine Storm Analysis System
echo ============================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Change to root directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "Storms\.venv" (
    echo Creating Python virtual environment...
    python -m venv "Storms\.venv"
)

REM Activate virtual environment
call "Storms\.venv\Scripts\activate.bat"

REM Install/upgrade requirements
echo Installing required packages...
pip install -r "Storms\requirements.txt" --quiet

REM Run the storm analysis
echo.
echo Starting storm analysis...
echo.
python "Storms\run_storm_analysis.py" %*

REM Keep window open if run without arguments
if "%1"=="" (
    echo.
    echo Analysis complete. Press any key to exit...
    pause >nul
)

deactivate

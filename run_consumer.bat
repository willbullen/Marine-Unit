@echo off
REM ===============================================
REM Consumer Data Export - Windows Batch Script
REM ===============================================
REM Builds consumer-ready CSVs from QC outputs
REM - Live logger only, QC-fail values removed, no indicator columns
REM - One CSV per buoy per year into Consumers/Data

echo Starting Consumer Data Export on Windows...
echo ===========================================

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating Python virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install/update dependencies (reuse QC requirements)
echo Installing required packages...
pip install -r "QC\requirements.txt"
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Run consumer export
echo.
echo Running consumer export...
echo ==========================
python "Consumers\Scripts\consumer_export.py"
if errorlevel 1 (
    echo ERROR: Consumer export failed
    pause
    exit /b 1
)

echo.
echo ==================================================
echo Consumer export completed successfully!
echo Outputs in 'Consumers\\Data' (one CSV per buoy-year)
echo ==================================================

pause



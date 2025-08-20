@echo off
REM ===============================================
REM Buoy QC Processing - Windows Batch Script
REM ===============================================
REM This script runs the buoy QC processing in a Python virtual environment
REM Generates separate CSV files and reports for each buoy-year combination
REM Run from the main project directory

echo Starting Buoy QC Processing on Windows...
echo =============================================

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating Python virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        echo Please ensure Python is installed and accessible
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

REM Install/update dependencies
echo Installing required packages...
pip install -r "QC Scripts\requirements.txt"
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Clear existing yearly output files to avoid confusion
echo Cleaning previous yearly output files...
if exist "QC Data\buoy_*_2023_*.csv" del "QC Data\buoy_*_2023_*.*"
if exist "QC Data\buoy_*_2024_*.csv" del "QC Data\buoy_*_2024_*.*"
if exist "QC Data\buoy_*_2025_*.csv" del "QC Data\buoy_*_2025_*.*"

REM Run QC processing
echo.
echo Running QC processing...
echo ========================
cd "QC Scripts"
python buoy_qc_processor.py
if errorlevel 1 (
    echo ERROR: QC processing failed
    cd ..
    pause
    exit /b 1
)

cd ..

echo.
echo ==================================================
echo QC Processing completed successfully!
echo.
echo Generated files are in the 'QC Data' folder:
echo - QC'd CSV files for each buoy station by year
echo - QC reports in markdown (*.md) and PDF (*.pdf) formats
echo - Color-coded visualization plots (*.png) for each year
echo.
echo File naming convention:
echo - buoy_STATION_YEAR_qcd.csv (e.g., buoy_62091_2023_qcd.csv)
echo - buoy_STATION_YEAR_qc_report.md
echo - buoy_STATION_YEAR_qc_overview.png
echo.
echo Scripts preserved in 'QC Scripts' folder for future use.
echo ==================================================

pause

@echo off
REM AutoID Validator - Windows Batch Script
REM Usage: double-click this file or run from command line

echo ============================================
echo   AutoID Validator - Bank & E-Wallet Validation
echo ============================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if dependencies are installed
python -c "import playwright" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo.
)

REM Run the validator
echo Starting AutoID Validator...
echo.
python main.py %*

echo.
pause

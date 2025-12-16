@echo off
REM ============================================================
REM Five Minds Setup Script for Windows
REM ============================================================
REM This script checks and sets up the environment for Five Minds
REM - Verifies Python installation
REM - Creates/activates virtual environment
REM - Installs required dependencies
REM ============================================================

setlocal EnableDelayedExpansion

echo.
echo ============================================================
echo         Five Minds - Setup Script
echo ============================================================
echo.

REM Check if Python is installed
echo [1/4] Checking Python installation...
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.8 or later from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo    Found Python %PYTHON_VERSION%

REM Check Python version is 3.8+
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Python 3.8 or later is required.
    echo Please update your Python installation.
    echo.
    pause
    exit /b 1
)

REM Check/Create virtual environment
echo.
echo [2/4] Setting up virtual environment...
if not exist "venv" (
    echo    Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: Failed to create virtual environment.
        echo.
        pause
        exit /b 1
    )
    echo    Virtual environment created.
) else (
    echo    Virtual environment already exists.
)

REM Activate virtual environment
echo.
echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to activate virtual environment.
    echo.
    pause
    exit /b 1
)
echo    Virtual environment activated.

REM Install dependencies
echo.
echo [4/4] Installing dependencies...
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to install dependencies.
    echo Please check your internet connection and try again.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo         Setup Complete!
echo ============================================================
echo.
echo You can now run Five Minds using: run.bat
echo.

REM Create a marker file to indicate setup is complete
echo %date% %time% > .setup_complete

endlocal
exit /b 0

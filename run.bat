@echo off
REM ============================================================
REM Five Minds Run Script for Windows
REM ============================================================
REM This script runs the Five Minds AI dev system
REM - Checks if setup is complete, runs setup if not
REM - Activates the virtual environment
REM - Launches Five Minds in interactive mode with UI
REM ============================================================

setlocal EnableDelayedExpansion

echo.
echo ============================================================
echo    Five Minds - Agentic AI Dev System
echo ============================================================
echo.

REM Check if setup has been completed
if not exist "venv" (
    echo Setup not complete. Running setup first...
    echo.
    call setup.bat
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: Setup failed. Please fix the issues and try again.
        echo.
        pause
        exit /b 1
    )
    echo.
)

REM Check if requirements are installed
if not exist ".setup_complete" (
    echo Dependencies may not be installed. Running setup...
    echo.
    call setup.bat
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: Setup failed. Please fix the issues and try again.
        echo.
        pause
        exit /b 1
    )
    echo.
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to activate virtual environment.
    echo Please run setup.bat first.
    echo.
    pause
    exit /b 1
)

REM Check if fiveminds package can be imported
python -c "import fiveminds" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Five Minds package not found. Running setup...
    echo.
    call setup.bat
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: Setup failed. Please fix the issues and try again.
        echo.
        pause
        exit /b 1
    )
    REM Re-activate after setup
    call venv\Scripts\activate.bat
)

REM Parse command line arguments
set "ARGS="
set "HAS_OBJECTIVE="

:parse_args
if "%~1"=="" goto run
if "%~1"=="--help" goto show_help
if "%~1"=="-h" goto show_help
set "ARGS=%ARGS% %1"
set "HAS_OBJECTIVE=1"
shift
goto parse_args

:show_help
echo Usage: run.bat [OPTIONS] [OBJECTIVE]
echo.
echo Options:
echo   --help, -h        Show this help message
echo   --interactive     Run in interactive mode (prompts for objective)
echo   --ui              Enable web UI dashboard
echo   --verbose         Enable verbose logging
echo   --repo PATH       Path to the repository (default: current directory)
echo   --max-runners N   Maximum number of parallel runners (default: 4)
echo.
echo Examples:
echo   run.bat                              Start in interactive mode with UI
echo   run.bat "Add user authentication"   Run with specified objective
echo   run.bat --ui "Your objective"        Run with UI enabled
echo.
goto end

:run
REM If no arguments provided, run in interactive mode with UI
if not defined HAS_OBJECTIVE (
    echo Starting Five Minds in interactive mode with UI...
    echo.
    python -m fiveminds.cli --interactive --ui
) else (
    echo Starting Five Minds...
    echo.
    python -m fiveminds.cli --ui%ARGS%
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Five Minds exited with an error.
    echo.
)

:end
endlocal
pause

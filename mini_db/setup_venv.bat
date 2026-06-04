@echo off
REM Kahatayn NPO System - Virtual Environment Setup
REM This script creates and configures the Python virtual environment

echo.
echo ========================================
echo Kahatayn System - Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment: npo_venv...
python -m venv npo_venv

if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo.
echo Activating virtual environment...
call npo_venv\Scripts\activate.bat

if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Upgrade pip
echo.
echo Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel

REM Install requirements
echo.
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Virtual environment created at: npo_venv\
echo To activate it in the future, run:
echo   npo_venv\Scripts\activate.bat
echo.
echo To run the application:
echo   python main.py
echo.
echo To build the .exe:
echo   run_build.bat
echo.
pause

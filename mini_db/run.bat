@echo off
REM Kahatayn NPO System - Development Runner
REM Automatically activates venv and runs the application

echo.
echo ========================================
echo Kahatayn System - Development Mode
echo ========================================
echo.

REM Check if venv exists
if not exist "npo_venv\Scripts\activate.bat" (
    echo Virtual environment not found!
    echo Running setup_venv.bat first...
    echo.
    call setup_venv.bat
)

REM Activate venv
call npo_venv\Scripts\activate.bat

REM Run the application
echo.
echo Starting Kahatayn application...
echo.
python main.py

REM On exit
echo.
echo Application closed.
pause

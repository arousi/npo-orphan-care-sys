@echo off
chcp 65001 >nul
title Kahatayn — Scanner

if not exist venv\Scripts\activate.bat (
    echo ERROR: Virtual environment not found.
    echo Run setup.bat first to install dependencies.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python convert.py
pause

@echo off
chcp 65001 >nul
title Kahatayn Setup

echo ============================================
echo   Kahatayn — Orphan Family Management System
echo   Setup Script (Batch)
echo ============================================
echo.

REM ----- Python -----
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [1/4] Python not found — installing via Chocolatey...
    where choco >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo     Installing Chocolatey first...
        @"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass ^
            -Command "[System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))" ^
            && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
    )
    choco install python -y
) else (
    echo [1/4] Python found: 
    python --version
)

REM ----- LibreOffice -----
echo.
echo [2/4] Installing LibreOffice (latest) via Chocolatey...
where choco >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo     Installing Chocolatey first...
    @"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass ^
        -Command "[System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))" ^
        && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
)
choco install libreoffice-fresh -y

REM ----- Virtual Environment -----
echo.
echo [3/4] Creating virtual environment...
python -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to create venv.
    pause
    exit /b 1
)

REM ----- Dependencies -----
echo.
echo [4/4] Installing dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Some packages failed to install. Check output above.
)

echo.
echo ============================================
echo   ✓ Setup complete!
echo.
echo   Quick start:
echo     run.bat              — activate env and run scanner
echo     cd mini_db ^&^& python main.py  — launch the desktop app
echo.
echo   One more step needed:
echo     Install the APSO extension in LibreOffice:
echo     https://extensions.libreoffice.org/en/extensions/show/apso-alternative-script-organizer-for-python
echo.
echo   Then deploy the macros:
echo     copy mini_db\kahatayn_macros.py "%APPDATA%\LibreOffice\4\user\Scripts\python\"
echo.
echo   Activate later:
echo     call venv\Scripts\activate
echo ============================================
echo.
pause

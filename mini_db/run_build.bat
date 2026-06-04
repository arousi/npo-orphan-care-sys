@echo off
REM Kahatayn NPO System - Build .exe
REM This script builds the portable .exe with bundled data files

echo.
echo ========================================
echo Kahatayn System - Building .exe
echo ========================================
echo.

REM Check if venv exists
if not exist "npo_venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup_venv.bat first
    pause
    exit /b 1
)

REM Activate venv
call npo_venv\Scripts\activate.bat

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "__pycache__" rmdir /s /q __pycache__

REM Build with PyInstaller
echo.
echo Building .exe with PyInstaller...
echo This may take a few minutes...
echo.

pyinstaller --onefile ^
    --windowed ^
    --name "Kahatayn" ^
    --add-data "data\orphanage_data.xlsx;data" ^
    --add-data "data\orphanage_data.ods;data" ^
    --add-data "data\orphanage.db;data" ^
    --hidden-import=tkinter ^
    --hidden-import=sqlalchemy ^
    --hidden-import=pandas ^
    --hidden-import=openpyxl ^
    --hidden-import=odf ^
    --hidden-import=reportlab ^
    main.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo The .exe is ready at:
echo   dist\Kahatayn.exe
echo.
echo Contents:
echo   - Kahatayn.exe (Main application)
echo   - data\ folder (sqlite db, xlsx, ods files)
echo.
echo To distribute:
echo   1. Copy entire dist\ folder to NPO computers
echo   2. Run Kahatayn.exe
echo   3. Backup/Export will allow them to modify files externally
echo.
pause

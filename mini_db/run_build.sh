#!/bin/bash
# Kahatayn NPO System - Build .exe (Linux/Mac)
# This script builds the portable .exe with bundled data files

echo ""
echo "========================================"
echo "Kahatayn System - Building .exe"
echo "========================================"
echo ""

# Check if venv exists
if [ ! -f "npo_venv/bin/activate" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run setup_venv.sh first"
    exit 1
fi

# Activate venv
source npo_venv/bin/activate

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist __pycache__

# Build with PyInstaller
echo ""
echo "Building executable with PyInstaller..."
echo "This may take a few minutes..."
echo ""

pyinstaller --onefile \
    --windowed \
    --name "Kahatayn" \
    --add-data "data/orphanage_data.xlsx:data" \
    --add-data "data/orphanage_data.ods:data" \
    --add-data "data/orphanage.db:data" \
    --hidden-import=tkinter \
    --hidden-import=sqlalchemy \
    --hidden-import=pandas \
    --hidden-import=openpyxl \
    --hidden-import=odf \
    --hidden-import=reportlab \
    main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Build failed!"
    exit 1
fi

echo ""
echo "========================================"
echo "Build Complete!"
echo "========================================"
echo ""
echo "The executable is ready at:"
echo "  dist/Kahatayn"
echo ""
echo "Contents:"
echo "  - Kahatayn (Main application)"
echo "  - data/ folder (sqlite db, xlsx, ods files)"
echo ""
echo "To distribute:"
echo "  1. Copy entire dist/ folder to NPO computers"
echo "  2. Run ./Kahatayn"
echo "  3. Backup/Export will allow them to modify files externally"
echo ""

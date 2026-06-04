<#
.SYNOPSIS
    Kahatayn — Run the workbook scanner
#>
$ErrorActionPreference = "Stop"
$Host.UI.RawUI.WindowTitle = "Kahatayn — Scanner"

if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found." -ForegroundColor Red
    Write-Host "Run setup.ps1 first to install dependencies." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

& .\venv\Scripts\Activate.ps1
python convert.py
Read-Host "`nPress Enter to exit"

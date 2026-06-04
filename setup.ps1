<#
.SYNOPSIS
    Kahatayn — Orphan Family Management System Setup Script
.DESCRIPTION
    Installs Python + LibreOffice via Chocolatey (if missing), creates a
    venv, and installs all pip dependencies.
.NOTES
    Run:  powershell -ExecutionPolicy Bypass -File setup.ps1
#>

$ErrorActionPreference = "Stop"
$Host.UI.RawUI.WindowTitle = "Kahatayn Setup"
$host.UI.RawUI.ForegroundColor = "Cyan"
Write-Host "============================================"
Write-Host "  Kahatayn — Orphan Family Management System"
Write-Host "  Setup Script (PowerShell)"
Write-Host "============================================"
$host.UI.RawUI.ForegroundColor = "Gray"

# ---- Python ----
Write-Host "`n[1/4] Checking Python..." -ForegroundColor Yellow
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Host "  Python not found — installing via Chocolatey..." -ForegroundColor Yellow
    $choco = Get-Command choco -ErrorAction SilentlyContinue
    if (-not $choco) {
        Write-Host "    Installing Chocolatey first..." -ForegroundColor Yellow
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = `
            [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression (
            (New-Object System.Net.WebClient).DownloadString(
                'https://community.chocolatey.org/install.ps1'
            )
        )
    }
    choco install python -y
    # Refresh PATH so the new python.exe is visible
    $env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + `
               [Environment]::GetEnvironmentVariable("Path","User")
} else {
    Write-Host "  Python found: $(& python --version)" -ForegroundColor Green
}

# ---- LibreOffice ----
Write-Host "`n[2/4] Installing LibreOffice (latest) via Chocolatey..." -ForegroundColor Yellow
$choco = Get-Command choco -ErrorAction SilentlyContinue
if (-not $choco) {
    Write-Host "    Installing Chocolatey first..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = `
        [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression (
        (New-Object System.Net.WebClient).DownloadString(
            'https://community.chocolatey.org/install.ps1'
        )
    )
}
choco install libreoffice-fresh -y
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: LibreOffice install failed or was cancelled. You can install manually from https://www.libreoffice.org/" -ForegroundColor Yellow
}

# ---- Virtual Environment ----
Write-Host "`n[3/4] Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create venv." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# ---- Dependencies ----
Write-Host "`n[4/4] Installing dependencies..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip | Out-Null
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Some packages failed to install. Check output above." -ForegroundColor Yellow
}

Write-Host "`n============================================" -ForegroundColor Green
Write-Host "  ✓ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "  Quick start:" -ForegroundColor White
Write-Host "    .\run.ps1              — activate env and run scanner"
Write-Host "    cd mini_db; python main.py  — launch the desktop app"
Write-Host ""
Write-Host "  One more step needed:" -ForegroundColor Yellow
Write-Host "    Install the APSO extension in LibreOffice:" -ForegroundColor Yellow
Write-Host "    https://extensions.libreoffice.org/en/extensions/show/apso-alternative-script-organizer-for-python" -ForegroundColor Yellow
Write-Host ""
Write-Host "    Then deploy the macros:" -ForegroundColor Yellow
Write-Host '    copy mini_db\kahatayn_macros.py "$env:APPDATA\LibreOffice\4\user\Scripts\python\"' -ForegroundColor Yellow
Write-Host ""
Write-Host "  Activate later:" -ForegroundColor White
Write-Host "    .\venv\Scripts\Activate"
Write-Host "============================================" -ForegroundColor Green
Read-Host "`nPress Enter to exit"

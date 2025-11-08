# Enhanced Email Sender - Automatic Setup Script
# Run as Administrator for full functionality

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Enhanced Email Sender - Setup" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "WARNING: Not running as administrator!" -ForegroundColor Yellow
    Write-Host "Right-click this file and select 'Run as Administrator' for full setup" -ForegroundColor Yellow
    Write-Host ""
}

# Get script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$wkhtmlPath = Join-Path $scriptPath "wkhtmltopdf"

Write-Host "Checking for wkhtmltopdf..." -ForegroundColor White

# Check if wkhtmltopdf is in PATH
$wkInPath = Get-Command wkhtmltopdf -ErrorAction SilentlyContinue
if ($wkInPath) {
    Write-Host "✓ wkhtmltopdf is already installed and in PATH!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Setup Complete! You can run Enhanced-Email-Sender.exe" -ForegroundColor Green
    pause
    exit 0
}

# Check for portable version
$portableExe = Join-Path $wkhtmlPath "bin\wkhtmltopdf.exe"
if (Test-Path $portableExe) {
    Write-Host "✓ Portable wkhtmltopdf found!" -ForegroundColor Green
    
    # Add to user PATH
    if ($isAdmin) {
        Write-Host "Adding to system PATH..." -ForegroundColor Yellow
        $binPath = Join-Path $wkhtmlPath "bin"
        $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
        if ($currentPath -notlike "*$binPath*") {
            [Environment]::SetEnvironmentVariable("Path", "$currentPath;$binPath", "Machine")
            Write-Host "✓ Added to system PATH!" -ForegroundColor Green
        }
    } else {
        Write-Host "Adding to session PATH..." -ForegroundColor Yellow
        $binPath = Join-Path $wkhtmlPath "bin"
        $env:Path += ";$binPath"
    }
    
    Write-Host ""
    Write-Host "Setup Complete! You can run Enhanced-Email-Sender.exe" -ForegroundColor Green
    pause
    exit 0
}

# Download and setup
Write-Host ""
Write-Host "====================================" -ForegroundColor Yellow
Write-Host "wkhtmltopdf Setup Required" -ForegroundColor Yellow
Write-Host "====================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "For full PDF/Image generation, wkhtmltopdf is needed." -ForegroundColor White
Write-Host ""
Write-Host "Option 1 (Recommended): Download from official site" -ForegroundColor Cyan
Write-Host "  Visit: https://wkhtmltopdf.org/downloads.html" -ForegroundColor White
Write-Host "  Download: 'Windows (MSVC 2015) 64-bit'" -ForegroundColor White
Write-Host "  Install it normally" -ForegroundColor White
Write-Host ""
Write-Host "Option 2: Extract portable version" -ForegroundColor Cyan
Write-Host "  Download the installer from above" -ForegroundColor White
Write-Host "  Extract to: $wkhtmlPath" -ForegroundColor White
Write-Host "  Then run this setup again" -ForegroundColor White
Write-Host ""
Write-Host "Note: The software will work without wkhtmltopdf," -ForegroundColor Gray
Write-Host "but PDF/Image quality will be reduced." -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to continue without wkhtmltopdf..." -ForegroundColor Yellow
pause

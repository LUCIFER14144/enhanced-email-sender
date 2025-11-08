@echo off
echo ============================================================
echo  Enhanced Email Sender - wkhtmltopdf Setup
echo ============================================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script requires Administrator privileges!
    echo Please right-click and select "Run as Administrator"
    echo.
    pause
    exit /b 1
)

echo Checking for wkhtmltopdf installer...
echo.

REM Check if installer exists
if exist "wkhtmltopdf\wkhtmltox-0.12.6-1.msvc2015-win64.exe" (
    echo Found installer: wkhtmltox-0.12.6-1.msvc2015-win64.exe
    echo Installing...
    start /wait wkhtmltopdf\wkhtmltox-0.12.6-1.msvc2015-win64.exe
) else (
    echo Installer not found in package. Downloading...
    echo.
    echo Opening download page...
    start https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox-0.12.6-1.msvc2015-win64.exe
    echo.
    echo Please:
    echo 1. Download the file from the opened browser
    echo 2. Place it in the wkhtmltopdf folder
    echo 3. Run this script again
    echo.
    echo OR install it directly from the downloaded file
    pause
    exit /b 0
)

echo.
echo Adding to PATH environment variable...

REM Add to system PATH
setx /M PATH "%PATH%;C:\Program Files\wkhtmltopdf\bin"

echo.
echo ============================================================
echo  Installation Complete!
echo ============================================================
echo.
echo IMPORTANT: Please restart your computer or close all
echo command prompts for the changes to take effect.
echo.
echo You can now run Enhanced-Email-Sender.exe
echo.
pause

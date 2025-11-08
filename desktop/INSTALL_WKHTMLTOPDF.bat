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

echo Installing wkhtmltopdf...
echo.

REM Check if installer exists
if exist "wkhtmltopdf\wkhtmltox-0.12.6-1.msvc2015-win64.exe" (
    echo Found installer: wkhtmltox-0.12.6-1.msvc2015-win64.exe
    start /wait wkhtmltopdf\wkhtmltox-0.12.6-1.msvc2015-win64.exe
) else (
    echo ERROR: wkhtmltopdf installer not found!
    echo Please download from: https://wkhtmltopdf.org/downloads.html
    echo Place it in the wkhtmltopdf folder
    echo.
    pause
    exit /b 1
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

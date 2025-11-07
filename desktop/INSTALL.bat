@echo off
REM Enhanced Email Sender - Quick Install Script
REM This script helps you set up the Enhanced Email Sender application

echo ===============================================
echo  Enhanced Email Sender - Installation
echo ===============================================
echo.

REM Check if the executable exists
if not exist "Enhanced-Email-Sender.exe" (
    echo [ERROR] Enhanced-Email-Sender.exe not found!
    echo.
    echo Please make sure this batch file is in the same folder as:
    echo   - Enhanced-Email-Sender.exe
    echo.
    echo Download the executable from:
    echo   https://perfected-vercelblasting.vercel.app
    echo.
    pause
    exit /b 1
)

echo [✓] Found Enhanced-Email-Sender.exe
echo.

REM Create desktop shortcut (optional)
echo Would you like to create a desktop shortcut?
echo Press Y for Yes, N for No
choice /C YN /N /M "Create shortcut? (Y/N): "

if errorlevel 2 goto skip_shortcut
if errorlevel 1 goto create_shortcut

:create_shortcut
echo.
echo [+] Creating desktop shortcut...

REM Get current directory
set CURRENT_DIR=%CD%

REM Create VBS script to generate shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%USERPROFILE%\Desktop\Enhanced Email Sender.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%CURRENT_DIR%\Enhanced-Email-Sender.exe" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%CURRENT_DIR%" >> CreateShortcut.vbs
echo oLink.Description = "Enhanced Email Sender - Cloud Email Management" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

REM Execute VBS script
cscript CreateShortcut.vbs //nologo

REM Cleanup
del CreateShortcut.vbs

echo [✓] Desktop shortcut created!
goto continue

:skip_shortcut
echo.
echo [i] Skipping desktop shortcut creation.

:continue
echo.
echo ===============================================
echo  Installation Complete!
echo ===============================================
echo.
echo Default Login Credentials:
echo   Username: demo
echo   Password: demo123
echo.
echo   OR
echo.
echo   Username: admin
echo   Password: admin123
echo.
echo Cloud API: https://perfected-vercelblasting.vercel.app
echo Admin Dashboard: https://perfected-vercelblasting.vercel.app/admin/dashboard
echo.
echo ===============================================
echo.

REM Ask if user wants to launch now
echo Would you like to launch Enhanced Email Sender now?
choice /C YN /N /M "Launch now? (Y/N): "

if errorlevel 2 goto end
if errorlevel 1 goto launch

:launch
echo.
echo [+] Launching Enhanced Email Sender...
start "" "Enhanced-Email-Sender.exe"
goto end

:end
echo.
echo Thank you for using Enhanced Email Sender!
echo.
pause

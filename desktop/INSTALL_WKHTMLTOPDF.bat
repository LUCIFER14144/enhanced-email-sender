@echo off
REM ═══════════════════════════════════════════════════════════════
REM   Enhanced Email Sender - wkhtmltopdf Auto Installer
REM ═══════════════════════════════════════════════════════════════

echo.
echo ═══════════════════════════════════════════════════════════════
echo   WKHTMLTOPDF INSTALLER
echo ═══════════════════════════════════════════════════════════════
echo.
echo This will install wkhtmltopdf for high-quality PDF/Image generation.
echo.
echo Administrator privileges required!
echo.
pause

REM Check if wkhtmltopdf folder exists
if not exist "%~dp0wkhtmltopdf" (
    echo.
    echo [ERROR] wkhtmltopdf folder not found!
    echo Please make sure you extracted all files from the ZIP.
    echo.
    pause
    exit /b 1
)

REM Check for installer in wkhtmltopdf folder
echo.
echo [INFO] Searching for wkhtmltopdf installer...
echo.

REM Look for the installer
for %%f in ("%~dp0wkhtmltopdf\*.exe" "%~dp0wkhtmltopdf\*.msi") do (
    set INSTALLER=%%f
    goto :found
)

REM If no installer found, provide download instructions
echo [WARNING] Installer not found in wkhtmltopdf folder.
echo.
echo Please download wkhtmltopdf from:
echo https://wkhtmltopdf.org/downloads.html
echo.
echo Download: wkhtmltopdf 0.12.6 (with patched qt) - Windows 64-bit
echo Save to: %~dp0wkhtmltopdf\
echo Then run this script again.
echo.
pause

REM Open download page
start https://wkhtmltopdf.org/downloads.html
exit /b 1

:found
echo [SUCCESS] Found installer: %INSTALLER%
echo.
echo Starting installation...
echo.

REM Run the installer
start /wait "" "%INSTALLER%" /S

echo.
echo ═══════════════════════════════════════════════════════════════
echo   INSTALLATION COMPLETE!
echo ═══════════════════════════════════════════════════════════════
echo.
echo wkhtmltopdf has been installed successfully.
echo.
echo IMPORTANT: You may need to restart Enhanced Email Sender
echo            for the changes to take effect.
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
pause

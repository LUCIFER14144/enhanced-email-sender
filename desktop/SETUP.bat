@echo off
echo ====================================
echo Enhanced Email Sender - Setup
echo ====================================
echo.
echo This will set up wkhtmltopdf for PDF/Image generation
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges...
) else (
    echo WARNING: Not running as administrator.
    echo Some features may not work properly.
    echo Right-click this file and select "Run as administrator"
    echo.
    pause
)

echo.
echo Checking for wkhtmltopdf...

REM Check if wkhtmltopdf is already installed
where wkhtmltopdf >nul 2>&1
if %errorLevel% == 0 (
    echo wkhtmltopdf is already installed!
    goto :END
)

echo wkhtmltopdf not found. Setting up portable version...
echo.

REM Create wkhtmltopdf directory if not exists
if not exist "%~dp0wkhtmltopdf" mkdir "%~dp0wkhtmltopdf"

REM Check if portable version exists
if exist "%~dp0wkhtmltopdf\bin\wkhtmltopdf.exe" (
    echo Portable wkhtmltopdf found!
    goto :SETPATH
)

echo.
echo ====================================
echo MANUAL DOWNLOAD REQUIRED
echo ====================================
echo.
echo Please download wkhtmltopdf manually from:
echo https://wkhtmltopdf.org/downloads.html
echo.
echo Download: "Windows (MSVC 2015) 64-bit"
echo Install it, or extract to: %~dp0wkhtmltopdf\
echo.
echo After installation, run this setup again.
echo.
pause
goto :END

:SETPATH
echo.
echo Adding wkhtmltopdf to PATH for this session...
set PATH=%~dp0wkhtmltopdf\bin;%PATH%
echo Done!
echo.

:END
echo.
echo ====================================
echo Setup Complete!
echo ====================================
echo.
echo You can now run Enhanced-Email-Sender.exe
echo.
pause

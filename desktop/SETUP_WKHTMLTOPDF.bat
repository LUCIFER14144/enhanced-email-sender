@echo off
echo ================================================
echo Enhanced Email Sender - wkhtmltopdf Setup
echo ================================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges...
) else (
    echo WARNING: Not running as administrator.
    echo Some features may not work correctly.
    echo Right-click this file and select "Run as administrator"
    pause
)

echo.
echo Installing wkhtmltopdf...
echo.

REM Check if wkhtmltopdf directory exists
if exist "%~dp0wkhtmltopdf\bin\wkhtmltopdf.exe" (
    echo wkhtmltopdf found in local directory.
    
    REM Add to PATH for current session
    set "PATH=%~dp0wkhtmltopdf\bin;%PATH%"
    
    REM Add to system PATH permanently
    echo Adding wkhtmltopdf to system PATH...
    setx PATH "%~dp0wkhtmltopdf\bin;%PATH%" /M 2>nul
    if %errorLevel% == 0 (
        echo Successfully added to system PATH!
    ) else (
        echo Could not add to system PATH. Run as administrator.
        setx PATH "%~dp0wkhtmltopdf\bin;%PATH%" 2>nul
        echo Added to user PATH instead.
    )
    
    echo.
    echo Testing wkhtmltopdf installation...
    "%~dp0wkhtmltopdf\bin\wkhtmltopdf.exe" --version
    
    echo.
    echo ================================================
    echo Setup Complete!
    echo ================================================
    echo.
    echo You can now run Enhanced-Email-Sender.exe
    echo.
) else (
    echo ERROR: wkhtmltopdf not found!
    echo Please ensure wkhtmltopdf folder is in the same directory.
    echo.
)

pause

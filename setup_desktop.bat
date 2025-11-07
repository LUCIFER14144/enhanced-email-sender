@echo off
echo =========================================
echo  Enhanced Email Sender - Desktop Setup
echo =========================================
echo.
echo Installing desktop application requirements...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Show Python version
echo Python version:
python --version
echo.

REM Upgrade pip first
echo [1/12] Upgrading pip...
python -m pip install --upgrade pip

REM Core requirements for desktop app
echo [2/12] Installing HTTP client...
python -m pip install requests==2.31.0

echo [3/12] Installing image processing...
python -m pip install pillow==10.1.0

echo [4/12] Installing Google API libraries...
python -m pip install google-auth==2.25.2
python -m pip install google-auth-oauthlib==1.1.0
python -m pip install google-auth-httplib2==2.0.0
python -m pip install google-api-python-client==2.110.0

echo [5/12] Installing HTML processing...
python -m pip install beautifulsoup4==4.12.2

echo [6/12] Installing PDF generation...
python -m pip install xhtml2pdf==0.2.13

echo [7/12] Installing additional PDF tools...
python -m pip install pdfkit==1.0.0

echo [8/12] Installing HTML to image conversion...
python -m pip install html2image==1.3.0

echo [9/12] Installing data generation...
python -m pip install faker==20.1.0
python -m pip install pycountry==22.3.13

echo [10/12] Installing data processing...
python -m pip install pandas==2.1.3
python -m pip install openpyxl==3.1.2

echo [11/12] Installing email validation...
python -m pip install email-validator==2.1.0

echo [12/12] Installing security libraries...
python -m pip install cryptography==41.0.8

echo.
echo =========================================
echo Installation completed!
echo =========================================
echo.

REM Test the installation
echo Testing installation...
python -c "
import sys
print(f'✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')

try:
    import tkinter
    print('✓ Tkinter: OK')
except ImportError:
    print('✗ Tkinter: FAILED - GUI not available')

try:
    import requests
    print('✓ Requests: OK')
except ImportError:
    print('✗ Requests: FAILED')

try:
    from PIL import Image
    print('✓ Pillow: OK')
except ImportError:
    print('✗ Pillow: FAILED')

try:
    from google.oauth2.credentials import Credentials
    print('✓ Google APIs: OK')
except ImportError:
    print('✗ Google APIs: FAILED')

print('\n📧 Enhanced Email Sender desktop app is ready!')
print('Run: python desktop/main.py')
"

echo.
echo =========================================
echo Setup Complete!
echo =========================================
echo.
echo To run the Enhanced Email Sender:
echo   python desktop/main.py
echo.
echo To create an executable:
echo   pip install pyinstaller
echo   pyinstaller --onefile --windowed desktop/main.py
echo.
echo The application will ask for your cloud login credentials
echo on first launch.
echo.
pause
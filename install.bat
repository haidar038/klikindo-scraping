@echo off
echo [INFO] Starting installation process...

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found! Please install Python 3.8+ and add it to PATH.
    pause
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [INFO] Creating virtual environment 'venv'...
    python -m venv venv
) else (
    echo [INFO] Virtual environment 'venv' already exists.
)

:: Activate venv and install requirements
echo [INFO] Activating virtual environment and installing packages...
call venv\Scripts\activate.bat

:: Install pip packages
pip install --upgrade pip
if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    echo [ERROR] requirements.txt not found!
    pause
    exit /b 1
)

:: Install Playwright browsers
echo [INFO] Installing Playwright browsers...
playwright install

echo.
echo [SUCCESS] Installation complete!
echo To run the scraper, verify your URLs in urls.txt and run:
echo     venv\Scripts\python scraper.py
echo.
pause

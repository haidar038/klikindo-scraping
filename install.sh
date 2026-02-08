#!/bin/bash

echo "[INFO] Starting installation process..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not found! Please install Python 3.8+."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "[INFO] Creating virtual environment 'venv'..."
    python3 -m venv venv
else
    echo "[INFO] Virtual environment 'venv' already exists."
fi

# Activate venv
source venv/bin/activate

# Install requirements
echo "[INFO] Installing packages..."
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "[ERROR] requirements.txt not found!"
    exit 1
fi

# Install Playwright browsers
echo "[INFO] Installing Playwright browsers..."
playwright install

echo ""
echo "[SUCCESS] Installation complete!"
echo "To run the scraper:"
echo "    source venv/bin/activate"
echo "    python scraper.py"

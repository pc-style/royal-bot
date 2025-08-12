#!/bin/bash

# Royal Match Bot Installation Script
# This script installs the bot and its dependencies

set -e  # Exit on any error

echo "🎮 Royal Match Bot - Installation Script"
echo "========================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher first."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python version $PYTHON_VERSION is too old. Please install Python $REQUIRED_VERSION or higher."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "✅ pip3 detected"

# Create virtual environment (optional)
read -p "🤔 Would you like to create a virtual environment? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Virtual environment created and activated"
    echo "💡 To activate it later, run: source venv/bin/activate"
fi

# Install dependencies
echo "📥 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Install system dependencies (Ubuntu/Debian)
if command -v apt-get &> /dev/null; then
    echo "🔧 Installing system dependencies..."
    
    # Update package list
    sudo apt-get update
    
    # Install OpenCV dependencies
    sudo apt-get install -y python3-opencv
    
    # Install Tesseract (optional, for OCR)
    read -p "🤔 Would you like to install Tesseract OCR for objective text recognition? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo apt-get install -y tesseract-ocr
        echo "✅ Tesseract OCR installed"
    fi
    
    echo "✅ System dependencies installed"
fi

# Test installation
echo "🧪 Testing installation..."
python3 test_basic.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Installation completed successfully!"
    echo ""
    echo "🚀 To get started:"
    echo "1. Take a screenshot of a Royal Match level"
    echo "2. Run: python3 main.py path/to/screenshot.png"
    echo "3. Or test the bot: python3 main.py --test"
    echo ""
    echo "📚 For more information, see README.md"
else
    echo "❌ Installation test failed. Please check the error messages above."
    exit 1
fi
#!/bin/bash
# YGG Torrent API Linux Setup Script

set -e

echo "🐧 YGG Torrent API Linux Setup"
echo "==============================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root"
   exit 1
fi

# Detect Linux distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
else
    echo "❌ Cannot detect Linux distribution"
    exit 1
fi

echo "📋 Detected OS: $OS $VER"

# Update package list
echo "🔄 Updating package list..."
sudo apt update || sudo yum update -y

# Install Python and pip
echo "🐍 Installing Python and pip..."
if command -v apt &> /dev/null; then
    sudo apt install -y python3 python3-pip python3-venv
elif command -v yum &> /dev/null; then
    sudo yum install -y python3 python3-pip
else
    echo "❌ Unsupported package manager"
    exit 1
fi

# Install Chrome/Chromium
echo "🌐 Installing Chrome/Chromium..."
if command -v apt &> /dev/null; then
    # Ubuntu/Debian - Try multiple methods
    echo "Installing Chrome for Ubuntu/Debian..."
    
    # Method 1: Install Google Chrome
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
    sudo apt update
    sudo apt install -y google-chrome-stable || echo "Google Chrome installation failed, trying Chromium..."
    
    # Method 2: Install Chromium as fallback
    sudo apt install -y chromium-browser || sudo apt install -y chromium || echo "Chromium installation also failed"
    
elif command -v yum &> /dev/null; then
    # CentOS/RHEL
    echo "Installing Chrome for CentOS/RHEL..."
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
    sudo yum localinstall -y google-chrome-stable_current_x86_64.rpm || echo "Google Chrome installation failed, trying Chromium..."
    rm -f google-chrome-stable_current_x86_64.rpm
    
    # Try Chromium as fallback
    sudo yum install -y chromium || echo "Chromium installation also failed"
    
elif command -v dnf &> /dev/null; then
    # Fedora
    echo "Installing Chrome for Fedora..."
    sudo dnf install -y google-chrome-stable || echo "Google Chrome installation failed, trying Chromium..."
    sudo dnf install -y chromium || echo "Chromium installation also failed"
    
elif command -v pacman &> /dev/null; then
    # Arch Linux
    echo "Installing Chrome for Arch Linux..."
    sudo pacman -S --noconfirm google-chrome || echo "Google Chrome installation failed, trying Chromium..."
    sudo pacman -S --noconfirm chromium || echo "Chromium installation also failed"
    
else
    echo "❌ Unsupported package manager. Please install Chrome/Chromium manually."
fi

# Install system dependencies
echo "📦 Installing system dependencies..."
if command -v apt &> /dev/null; then
    sudo apt install -y wget curl unzip
elif command -v yum &> /dev/null; then
    sudo yum install -y wget curl unzip
fi

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv ygg_env

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source ygg_env/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements_api.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs data

# Set permissions
echo "🔐 Setting permissions..."
chmod +x ygg_api.py

# Verify Chrome installation
echo "🔍 Verifying Chrome/Chromium installation..."
if command -v google-chrome &> /dev/null; then
    echo "✅ Google Chrome found: $(which google-chrome)"
elif command -v chromium &> /dev/null; then
    echo "✅ Chromium found: $(which chromium)"
elif command -v chromium-browser &> /dev/null; then
    echo "✅ Chromium Browser found: $(which chromium-browser)"
else
    echo "⚠️  Warning: Chrome/Chromium not found in PATH"
    echo "   You may need to install it manually or check your installation"
fi

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "🚀 To run the API:"
echo "   1. Activate virtual environment: source ygg_env/bin/activate"
echo "   2. Start the API: python3 ygg_api.py"
echo ""
echo "🌐 API will be available at: http://localhost:8080"
echo ""
echo "📖 For more information, see API_README.md"

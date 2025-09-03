#!/bin/bash

# YGG Torrent Parser - Ubuntu Deployment Script
# This script sets up the YGG Torrent parser on Ubuntu

set -e  # Exit on any error

echo "🚀 YGG Torrent Parser - Ubuntu Deployment"
echo "=========================================="

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python 3 and pip
echo "🐍 Installing Python 3 and pip..."
sudo apt install -y python3 python3-pip python3-venv

# Install Chrome and ChromeDriver for Selenium
echo "🌐 Installing Google Chrome..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install -y google-chrome-stable

# Install ChromeDriver
echo "🔧 Installing ChromeDriver..."
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d'.' -f1-3)
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}")
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
sudo unzip /tmp/chromedriver.zip -d /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
rm /tmp/chromedriver.zip

# Install system dependencies
echo "📚 Installing system dependencies..."
sudo apt install -y curl wget unzip xvfb

# Create virtual environment
echo "🔧 Creating Python virtual environment..."
python3 -m venv ygg_parser_env
source ygg_parser_env/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p downloads
mkdir -p data

# Set permissions
echo "🔐 Setting permissions..."
chmod +x *.py
chmod 755 downloads data logs

# Create systemd service file
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/ygg-parser.service > /dev/null <<EOF
[Unit]
Description=YGG Torrent Parser Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/ygg_parser_env/bin
ExecStart=$(pwd)/ygg_parser_env/bin/python3 ygg_parser_complete.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create cron job for automated runs
echo "⏰ Setting up cron job..."
(crontab -l 2>/dev/null; echo "0 */6 * * * cd $(pwd) && $(pwd)/ygg_parser_env/bin/python3 ygg_parser_complete.py >> logs/cron.log 2>&1") | crontab -

# Create configuration file
echo "⚙️ Creating configuration file..."
cat > config_ubuntu.py <<EOF
# Ubuntu-specific configuration
import os

# Base configuration
BASE_URL = "https://www.yggtorrent.top"
PASSKEY = "DJdLXYBi2WmyQB0PdNWZ8u9RZEnTqiXT"

# Ubuntu-specific settings
HEADLESS_MODE = True  # Always run headless on server
CHROME_BINARY_PATH = "/usr/bin/google-chrome"
CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver"

# Paths
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
DATA_DIR = os.path.join(os.getcwd(), "data")
LOG_DIR = os.path.join(os.getcwd(), "logs")

# Request settings
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 2

# Available subcategories
SUBCATEGORIES = {
    'Nintendo Games': 2163,
    'PlayStation Games': 2145,
    'Xbox Games': 2146,
    'PC Games': 2142,
    'Movies': 2188,
    'TV Shows': 2189,
    'Music': 2190,
    'Software': 2144,
    'Books': 2191,
    'Anime': 2192
}
EOF

# Create startup script
echo "🚀 Creating startup script..."
cat > start_parser.sh <<EOF
#!/bin/bash
cd $(pwd)
source ygg_parser_env/bin/activate
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
python3 ygg_parser_complete.py
EOF
chmod +x start_parser.sh

# Create monitoring script
echo "📊 Creating monitoring script..."
cat > monitor.sh <<EOF
#!/bin/bash
echo "YGG Parser Status Monitor"
echo "========================"
echo "Service Status:"
systemctl status ygg-parser.service --no-pager
echo ""
echo "Recent Logs:"
tail -n 20 logs/cron.log 2>/dev/null || echo "No logs found"
echo ""
echo "Disk Usage:"
du -sh downloads/ data/ logs/ 2>/dev/null || echo "Directories not found"
echo ""
echo "Running Processes:"
ps aux | grep python | grep ygg
EOF
chmod +x monitor.sh

echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Update config_ubuntu.py with your credentials"
echo "2. Test the parser: ./start_parser.sh"
echo "3. Start the service: sudo systemctl start ygg-parser"
echo "4. Enable auto-start: sudo systemctl enable ygg-parser"
echo "5. Monitor: ./monitor.sh"
echo ""
echo "🔧 Useful commands:"
echo "- Start service: sudo systemctl start ygg-parser"
echo "- Stop service: sudo systemctl stop ygg-parser"
echo "- View logs: sudo journalctl -u ygg-parser -f"
echo "- Monitor: ./monitor.sh"
echo ""
echo "📁 Files created:"
echo "- config_ubuntu.py (Ubuntu-specific config)"
echo "- start_parser.sh (Startup script)"
echo "- monitor.sh (Monitoring script)"
echo "- /etc/systemd/system/ygg-parser.service (System service)"
echo ""
echo "🎯 The parser is now ready to run on Ubuntu!"

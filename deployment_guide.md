# YGG Torrent Parser - Ubuntu Deployment Guide

This guide will help you deploy the YGG Torrent parser on a remote Ubuntu server.

## 🚀 Quick Deployment

### Method 1: Automated Script (Recommended)

1. **Upload files to your Ubuntu server:**
   ```bash
   scp -r YGGparser/ user@your-server:/home/user/
   ```

2. **SSH into your server:**
   ```bash
   ssh user@your-server
   ```

3. **Run the deployment script:**
   ```bash
   cd YGGparser
   chmod +x deploy.sh
   ./deploy.sh
   ```

4. **Configure your credentials:**
   ```bash
   nano config_ubuntu.py
   # Update PASSKEY with your actual passkey
   ```

5. **Set environment variables:**
   ```bash
   export YGG_COOKIES="your_cookies_here"
   ```

6. **Test the parser:**
   ```bash
   ./start_parser.sh
   ```

7. **Start the service:**
   ```bash
   sudo systemctl start ygg-parser
   sudo systemctl enable ygg-parser
   ```

### Method 2: Docker Deployment

1. **Upload files to your Ubuntu server:**
   ```bash
   scp -r YGGparser/ user@your-server:/home/user/
   ```

2. **SSH into your server:**
   ```bash
   ssh user@your-server
   ```

3. **Install Docker:**
   ```bash
   sudo apt update
   sudo apt install -y docker.io docker-compose
   sudo systemctl start docker
   sudo systemctl enable docker
   sudo usermod -aG docker $USER
   ```

4. **Configure environment:**
   ```bash
   cd YGGparser
   cp env.example .env
   nano .env
   # Fill in your YGG_COOKIES and YGG_PASSKEY
   ```

5. **Build and run:**
   ```bash
   docker-compose up -d
   ```

## 📋 Manual Installation

If you prefer to install manually:

### 1. System Requirements

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3 and pip
sudo apt install -y python3 python3-pip python3-venv

# Install Chrome and ChromeDriver
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install -y google-chrome-stable

# Install ChromeDriver
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d'.' -f1-3)
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}")
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
sudo unzip /tmp/chromedriver.zip -d /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
rm /tmp/chromedriver.zip

# Install system dependencies
sudo apt install -y curl wget unzip xvfb
```

### 2. Python Environment

```bash
# Create virtual environment
python3 -m venv ygg_parser_env
source ygg_parser_env/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Create configuration file
cp config.py config_ubuntu.py
nano config_ubuntu.py
# Update with your credentials
```

### 4. Service Setup

```bash
# Create systemd service
sudo tee /etc/systemd/system/ygg-parser.service > /dev/null <<EOF
[Unit]
Description=YGG Torrent Parser Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/ygg_parser_env/bin
ExecStart=$(pwd)/ygg_parser_env/bin/python3 ygg_parser_ubuntu.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable ygg-parser
sudo systemctl start ygg-parser
```

## 🔧 Configuration

### Environment Variables

Set these environment variables for the parser:

```bash
# Required
export YGG_COOKIES="cf_clearance=...; account_created=true; yggxf_user=...; a3_promo_details=...; ygg_=..."
export YGG_PASSKEY="your_passkey_here"

# Optional
export YGG_CATEGORIES="2163,2145,2146"  # Specific categories
export YGG_INTERVAL="6"                 # Hours between runs
export YGG_MAX_TORRENTS="100"           # Max torrents per category
export YGG_DEBUG="false"                # Debug logging
```

### Getting Cookies

1. **Log into YGG Torrent in your browser**
2. **Open Developer Tools (F12)**
3. **Go to Application tab → Cookies → https://www.yggtorrent.top**
4. **Copy all cookie values in format: `name1=value1; name2=value2`**

## 📊 Monitoring

### Service Status

```bash
# Check service status
sudo systemctl status ygg-parser

# View logs
sudo journalctl -u ygg-parser -f

# View application logs
tail -f logs/ygg_parser.log
```

### Monitoring Script

```bash
# Run monitoring script
./monitor.sh
```

### Cron Jobs

The deployment script sets up a cron job to run every 6 hours:

```bash
# View cron jobs
crontab -l

# Edit cron jobs
crontab -e
```

## 🐳 Docker Commands

```bash
# Build image
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart
```

## 📁 File Structure

After deployment, your directory structure will be:

```
YGGparser/
├── ygg_parser_ubuntu.py      # Main parser for Ubuntu
├── config_ubuntu.py          # Ubuntu-specific configuration
├── requirements.txt          # Python dependencies
├── deploy.sh                 # Deployment script
├── start_parser.sh           # Startup script
├── monitor.sh                # Monitoring script
├── docker-compose.yml        # Docker configuration
├── Dockerfile                # Docker image definition
├── env.example               # Environment variables example
├── data/                     # JSON output files
├── logs/                     # Log files
├── downloads/                # Downloaded torrent files
└── ygg_parser_env/           # Python virtual environment
```

## 🔍 Troubleshooting

### Common Issues

1. **ChromeDriver not found:**
   ```bash
   # Check ChromeDriver installation
   which chromedriver
   chromedriver --version
   ```

2. **Permission denied:**
   ```bash
   # Fix permissions
   chmod +x *.py
   chmod 755 data logs downloads
   ```

3. **Service not starting:**
   ```bash
   # Check service logs
   sudo journalctl -u ygg-parser -f
   
   # Check configuration
   sudo systemctl status ygg-parser
   ```

4. **Authentication failed:**
   ```bash
   # Verify cookies
   echo $YGG_COOKIES
   
   # Test manually
   python3 ygg_parser_ubuntu.py
   ```

### Log Files

- **System logs:** `/var/log/syslog`
- **Service logs:** `sudo journalctl -u ygg-parser`
- **Application logs:** `logs/ygg_parser.log`
- **Cron logs:** `logs/cron.log`

## 🔒 Security Considerations

1. **Use environment variables for sensitive data**
2. **Restrict file permissions**
3. **Use a non-root user for the service**
4. **Regularly update dependencies**
5. **Monitor logs for suspicious activity**

## 📈 Performance Optimization

1. **Adjust cron frequency based on your needs**
2. **Limit number of categories processed**
3. **Use SSD storage for better I/O performance**
4. **Monitor system resources**

## 🆘 Support

If you encounter issues:

1. Check the logs first
2. Verify your configuration
3. Test manually before running as service
4. Check system resources (CPU, memory, disk)

## 📝 Notes

- The parser runs in headless mode on Ubuntu servers
- Cookies may expire and need to be refreshed periodically
- The service automatically restarts on failure
- All output is saved to JSON files in the `data/` directory

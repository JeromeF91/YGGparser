# YGG Torrent API - Linux Setup Guide

This guide helps you set up the YGG Torrent API on a Linux machine.

## 🚀 Quick Setup

### **Option 1: Automated Setup (Recommended)**
```bash
# Download and run the setup script
chmod +x setup_linux.sh
./setup_linux.sh
```

### **Option 2: Manual Setup**
```bash
# 1. Install Python and pip
sudo apt update
sudo apt install python3 python3-pip python3-venv

# 2. Install Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install google-chrome-stable

# 3. Create virtual environment
python3 -m venv ygg_env
source ygg_env/bin/activate

# 4. Install dependencies
pip install -r requirements_api.txt

# 5. Run the API
python3 ygg_api.py
```

## 📋 Prerequisites

- **Linux Distribution**: Ubuntu 18.04+, Debian 9+, CentOS 7+, or RHEL 7+
- **Python**: 3.7 or higher
- **Memory**: At least 2GB RAM
- **Storage**: At least 1GB free space

## 🔧 Manual Installation Steps

### **1. Install System Dependencies**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv wget curl unzip

# CentOS/RHEL
sudo yum update -y
sudo yum install python3 python3-pip wget curl unzip
```

### **2. Install Google Chrome**
```bash
# Ubuntu/Debian
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install google-chrome-stable

# CentOS/RHEL
wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
sudo yum localinstall google-chrome-stable_current_x86_64.rpm
```

### **3. Set Up Python Environment**
```bash
# Create virtual environment
python3 -m venv ygg_env

# Activate virtual environment
source ygg_env/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements_api.txt
```

### **4. Create Directories**
```bash
mkdir -p logs data
chmod +x ygg_api.py
```

## 🚀 Running the API

### **Start the API**
```bash
# Activate virtual environment
source ygg_env/bin/activate

# Start the API
python3 ygg_api.py
```

### **Test the API**
```bash
# Health check
curl http://localhost:8080/health

# Authenticate
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"your_username","password":"your_password"}'
```

## 🔧 Troubleshooting

### **Common Issues**

#### **1. ModuleNotFoundError: No module named 'flask'**
```bash
# Solution: Install dependencies
source ygg_env/bin/activate
pip install -r requirements_api.txt
```

#### **2. Chrome/Chromium not found**
```bash
# Check if Chrome is installed
google-chrome --version

# If not installed, install it:
sudo apt install google-chrome-stable
```

#### **3. Permission denied**
```bash
# Make scripts executable
chmod +x ygg_api.py
chmod +x setup_linux.sh
```

#### **4. Port 8080 already in use**
```bash
# Check what's using port 8080
sudo netstat -tlnp | grep :8080

# Kill the process or change port in ygg_api.py
```

### **Headless Mode Issues**
If you're running on a server without a display, the API will automatically use headless mode. However, you might need to install additional dependencies:

```bash
# Install X11 dependencies for headless mode
sudo apt install xvfb

# Or run with virtual display
xvfb-run -a python3 ygg_api.py
```

## 🔒 Security Considerations

### **Firewall Setup**
```bash
# Allow port 8080 (if needed for remote access)
sudo ufw allow 8080

# Or use iptables
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
```

### **User Permissions**
```bash
# Create dedicated user (recommended)
sudo useradd -m -s /bin/bash yggparser
sudo su - yggparser

# Run API as non-root user
python3 ygg_api.py
```

## 📊 System Requirements

### **Minimum Requirements**
- **CPU**: 1 core
- **RAM**: 2GB
- **Storage**: 1GB
- **OS**: Linux (Ubuntu 18.04+, Debian 9+, CentOS 7+)

### **Recommended Requirements**
- **CPU**: 2+ cores
- **RAM**: 4GB+
- **Storage**: 5GB+
- **OS**: Ubuntu 20.04+ or CentOS 8+

## 🚀 Production Deployment

### **Using systemd (Recommended)**
```bash
# Create systemd service file
sudo nano /etc/systemd/system/ygg-api.service
```

```ini
[Unit]
Description=YGG Torrent API
After=network.target

[Service]
Type=simple
User=yggparser
WorkingDirectory=/home/yggparser/YGGparser
Environment=PATH=/home/yggparser/YGGparser/ygg_env/bin
ExecStart=/home/yggparser/YGGparser/ygg_env/bin/python ygg_api.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable ygg-api
sudo systemctl start ygg-api

# Check status
sudo systemctl status ygg-api
```

### **Using PM2 (Alternative)**
```bash
# Install PM2
npm install -g pm2

# Start with PM2
pm2 start ygg_api.py --name ygg-api --interpreter python3

# Save PM2 configuration
pm2 save
pm2 startup
```

## 📝 Logs and Monitoring

### **View Logs**
```bash
# API logs
tail -f logs/api.log

# System logs (if using systemd)
sudo journalctl -u ygg-api -f
```

### **Monitor Resources**
```bash
# Check memory usage
free -h

# Check disk usage
df -h

# Check running processes
ps aux | grep ygg_api
```

## 🔄 Updates

### **Update the API**
```bash
# Pull latest changes
git pull origin main

# Update dependencies
source ygg_env/bin/activate
pip install -r requirements_api.txt --upgrade

# Restart API
sudo systemctl restart ygg-api
```

## 📞 Support

If you encounter issues:

1. Check the logs: `tail -f logs/api.log`
2. Verify dependencies: `pip list`
3. Test Chrome: `google-chrome --version`
4. Check system resources: `free -h` and `df -h`

For more help, see the main `API_README.md` file.

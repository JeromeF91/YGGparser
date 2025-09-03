# YGG Torrent Parser

A Python tool to parse torrent information from YGG Torrent RSS feeds with Cloudflare protection bypass capabilities.

## Features

- **Cloudflare Bypass**: Uses `cloudscraper` to handle Cloudflare protection
- **RSS Feed Parsing**: Parses YGG Torrent RSS feeds to extract torrent metadata
- **Torrent Download**: Downloads actual `.torrent` files
- **Multiple Categories**: Support for various subcategories (games, movies, software, etc.)
- **JSON Export**: Save torrent information to JSON files
- **Filtering**: Filter torrents by seeds, size, and other criteria

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd YGGparser
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### Method 1: Using Authentication (Recommended)

The RSS feed requires authentication. You have several options:

#### Option A: Full Authentication
Use `ygg_parser_auth.py` with your username and password:
```python
from ygg_parser_auth import YGGParserAuth

parser = YGGParserAuth()
parser.authenticate("your_username", "your_password")
```

#### Option B: Manual Cookie Extraction
Use `ygg_parser_cookies.py` with cookies from your browser:
1. Log in to YGG Torrent in your browser
2. Open Developer Tools (F12)
3. Go to Application/Storage tab
4. Copy cookies for yggtorrent.top
5. Use them with the parser

### Method 2: Passkey Only (May not work due to Cloudflare)

1. Edit `config.py` and replace the `PASSKEY` with your actual YGG Torrent passkey:
```python
PASSKEY = "your_actual_passkey_here"
```

2. The passkey can be found in your YGG Torrent account settings.

## Usage

### Basic Usage

#### With Authentication
```python
from ygg_parser_auth import YGGParserAuth

# Create parser and authenticate
parser = YGGParserAuth()
parser.authenticate("your_username", "your_password")

# Get Nintendo games (subcategory 2163)
rss_content = parser.get_rss_feed(2163, "your_passkey")
torrents = parser.parse_rss_feed(rss_content)

# Display torrents
for torrent in torrents[:5]:
    print(f"Title: {torrent['title']}")
    print(f"Size: {torrent['size']}")
    print(f"Seeds: {torrent['seeds']}")
    print("-" * 50)
```

#### With Cookies
```python
from ygg_parser_cookies import YGGParserCookies

# Create parser and set cookies
parser = YGGParserCookies()
parser.set_cookies_from_browser("cookie1=value1; cookie2=value2")

# Get Nintendo games (subcategory 2163)
rss_content = parser.get_rss_feed(2163, "your_passkey")
torrents = parser.parse_rss_feed(rss_content)
```

### Download Torrent Files

```python
# Download a specific torrent file
torrent_content = parser.get_torrent_file(
    torrent_url,
    "my_torrent.torrent"
)
```

### Available Categories

The parser supports various subcategories:

- Nintendo Games: 2163
- PlayStation Games: 2145
- Xbox Games: 2146
- PC Games: 2142
- Movies: 2188
- TV Shows: 2189
- Music: 2190
- Software: 2144
- Books: 2191
- Anime: 2192

### Run Examples

```bash
# Complete parser with multiple authentication methods (RECOMMENDED)
python3 ygg_parser_complete.py

# Working example with manual cookie extraction
python3 working_example.py

# Automated Selenium authentication (requires ChromeDriver)
python3 ygg_selenium_auth.py

# Manual cookie test
python3 manual_cookie_test.py

# Try the cookie-based approach
python3 ygg_parser_cookies.py

# Try the full authentication approach
python3 ygg_parser_auth.py

# Try the original approach (may not work due to Cloudflare)
python3 ygg_parser.py
```

## Quick Start Guide

### Method 1: Automated Authentication (Recommended)

1. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Install ChromeDriver (for Selenium):**
   - Download from: https://chromedriver.chromium.org/
   - Make sure it's in your PATH

3. **Run the complete parser:**
   ```bash
   python3 ygg_parser_complete.py
   ```

4. **Choose authentication method:**
   - Option 1: Selenium (handles Cloudflare automatically)
   - Option 2: Manual cookies (from browser)

### Method 2: Manual Cookie Extraction

1. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Get cookies from your browser:**
   - Go to https://www.yggtorrent.top
   - Log in with your credentials
   - Open Developer Tools (F12)
   - Go to Application tab → Cookies → https://www.yggtorrent.top
   - Copy all cookie values

3. **Run the working example:**
   ```bash
   python3 working_example.py
   ```

4. **Follow the prompts to paste your cookies and enter your passkey**

## RSS Feed URL Format

The RSS feed URL follows this format:
```
https://www.yggtorrent.top/rss?action=generate&type=subcat&id={subcat_id}&passkey={passkey}
```

Where:
- `subcat_id`: The subcategory ID (e.g., 2163 for Nintendo games)
- `passkey`: Your YGG Torrent passkey

## Dependencies

- `requests`: HTTP library
- `cloudscraper`: Cloudflare bypass library
- `beautifulsoup4`: HTML parsing
- `lxml`: XML parsing

## 🚀 Remote Ubuntu Deployment

### Quick Deployment

1. **Deploy to remote Ubuntu server:**
   ```bash
   python3 remote_deploy.py your-server.com username
   ```

2. **Or create deployment package:**
   ```bash
   python3 remote_deploy.py localhost testuser --package-only
   ```

3. **Manual deployment:**
   ```bash
   scp -r YGGparser/ user@your-server:/home/user/
   ssh user@your-server
   cd YGGparser
   chmod +x deploy.sh
   ./deploy.sh
   ```

### Docker Deployment

```bash
# Configure environment
cp env.example .env
nano .env  # Fill in your credentials

# Deploy with Docker
docker-compose up -d
```

### Server Features

- ✅ **Automated Installation**: Installs all dependencies automatically
- ✅ **System Service**: Runs as a systemd service with auto-restart
- ✅ **Cron Jobs**: Automated runs every 6 hours
- ✅ **Logging**: Comprehensive logging system
- ✅ **Monitoring**: Built-in monitoring scripts
- ✅ **Docker Support**: Full Docker containerization
- ✅ **Headless Mode**: Optimized for server environments

### Configuration

Set environment variables on your server:

```bash
export YGG_COOKIES="your_cookies_here"
export YGG_PASSKEY="your_passkey_here"
```

## 📥 Torrent Download Features

### Enhanced Download Functionality

The parser now includes comprehensive torrent file downloading capabilities:

- **🔄 Single Downloads**: Download individual torrent files with progress tracking
- **⚡ Batch Downloads**: Download multiple torrents in parallel
- **🎯 Criteria-Based**: Filter downloads by seeds, size, keywords
- **📊 Progress Tracking**: Real-time download progress monitoring
- **📈 Statistics**: Track download history and storage usage
- **🛡️ Error Handling**: Robust error handling and retry logic

### Download Examples

```python
from ygg_parser_with_downloads import YGGParserWithDownloads

parser = YGGParserWithDownloads()
parser.authenticate_with_cookies("your_cookies_here")

# Get torrents
torrents = parser.parse_rss_feed(rss_content)

# Download single torrent
filepath = parser.download_torrent_file(torrents[0]['torrent_link'])

# Batch download
results = parser.download_torrents_batch(torrents, max_workers=3)

# Criteria-based download
results = parser.download_torrents_by_criteria(
    torrents,
    min_seeds=5,
    max_size_mb=5000,
    keywords=['game', 'hd']
)
```

### Download Configuration

Set environment variables for automatic downloads:

```bash
export YGG_DOWNLOAD_ENABLED=true
export YGG_MIN_SEEDS=5
export YGG_MAX_SIZE_MB=5000
export YGG_KEYWORDS=game,hd,1080p
```

## 📋 Project Files

### Core Files
- `ygg_parser.py` - Main parser with download functionality
- `ygg_auth.py` - Selenium-based authentication system
- `ygg_downloader.py` - Complete authentication + download workflow
- `ygg_cookies.py` - Simple cookie extraction tool

### Deployment Files
- `deploy.sh` - Automated Ubuntu deployment script
- `ygg_parser_ubuntu.py` - Ubuntu-optimized parser
- `docker-compose.yml` - Docker deployment configuration
- `Dockerfile` - Docker image definition
- `remote_deploy.py` - Remote deployment automation
- `deployment_guide.md` - Complete deployment guide

### Configuration
- `config.py` - Configuration settings
- `requirements.txt` - Python dependencies
- `env.example` - Environment variables example

## Notes

- Make sure you have a valid YGG Torrent account and passkey
- The parser handles Cloudflare protection automatically
- RSS feeds may have rate limits, so use responsibly
- Always respect the website's terms of service
- For server deployment, cookies may need periodic refresh

## License

This project is for educational purposes only. Please respect YGG Torrent's terms of service and use responsibly.
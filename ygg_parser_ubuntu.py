#!/usr/bin/env python3
"""
YGG Torrent Parser optimized for Ubuntu server deployment
"""

import requests
import xml.etree.ElementTree as ET
import json
import time
import re
import os
import logging
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from datetime import datetime

try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class YGGParserUbuntu:
    """YGG Torrent Parser optimized for Ubuntu server deployment."""
    
    def __init__(self, base_url: str = "https://www.yggtorrent.top"):
        self.base_url = base_url
        self.session = None
        self.authenticated = False
        self.cookies = {}
        self.logger = self._setup_logging()
        self._setup_session()
    
    def _setup_logging(self):
        """Setup logging for server deployment."""
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Setup logging
        logger = logging.getLogger('ygg_parser')
        logger.setLevel(logging.INFO)
        
        # Create file handler
        file_handler = logging.FileHandler('logs/ygg_parser.log')
        file_handler.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _setup_session(self):
        """Setup session with cloudscraper."""
        if CLOUDSCRAPER_AVAILABLE:
            try:
                self.session = cloudscraper.create_scraper(
                    browser={
                        'browser': 'chrome',
                        'platform': 'linux',
                        'mobile': False
                    }
                )
                self.logger.info("✅ Using cloudscraper session")
            except Exception as e:
                self.logger.warning(f"⚠ Cloudscraper failed: {e}")
                self.session = requests.Session()
        else:
            self.session = requests.Session()
        
        # Set headers optimized for Ubuntu
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def authenticate_with_selenium(self, username: str, password: str, headless: bool = True) -> bool:
        """
        Authenticate using Selenium optimized for Ubuntu server.
        
        Args:
            username: YGG Torrent username
            password: YGG Torrent password
            headless: Run browser in headless mode (always True on server)
            
        Returns:
            True if authentication successful, False otherwise
        """
        if not SELENIUM_AVAILABLE:
            self.logger.error("❌ Selenium not available. Install with: pip install selenium")
            return False
        
        driver = None
        try:
            self.logger.info("🚀 Starting Selenium authentication...")
            
            # Setup Chrome options for Ubuntu server
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Always headless on server
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-images')
            chrome_options.add_argument('--disable-javascript')  # We'll enable it later if needed
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Create driver
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Navigate to login page
            self.logger.info("📄 Navigating to login page...")
            login_url = f"{self.base_url}/user/login"
            self.driver.get(login_url)
            
            # Wait for Cloudflare challenge
            wait = WebDriverWait(self.driver, 60)
            if "Just a moment" in self.driver.title:
                self.logger.info("⏳ Cloudflare challenge detected, waiting...")
                wait.until(lambda d: "Just a moment" not in d.title)
                self.logger.info("✅ Cloudflare challenge completed!")
            
            time.sleep(3)
            
            # Find and fill login form
            username_field = self.driver.find_element(By.CSS_SELECTOR, "input[name='id']")
            password_field = self.driver.find_element(By.CSS_SELECTOR, "input[name='pass']")
            
            username_field.clear()
            username_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)
            
            # Submit form
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
            submit_button.click()
            
            # Wait for login
            time.sleep(5)
            
            # Check if successful
            page_source = self.driver.page_source.lower()
            if 'logout' in page_source or 'déconnexion' in page_source:
                self.logger.info("✅ Selenium authentication successful!")
                
                # Get cookies
                selenium_cookies = self.driver.get_cookies()
                self.cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
                
                # Transfer cookies to requests session
                for name, value in self.cookies.items():
                    self.session.cookies.set(name, value)
                
                self.authenticated = True
                return True
            else:
                self.logger.error("❌ Selenium authentication failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Selenium authentication error: {e}")
            return False
        finally:
            if driver:
                driver.quit()
    
    def authenticate_with_cookies(self, cookie_string: str) -> bool:
        """
        Authenticate using cookie string from browser.
        
        Args:
            cookie_string: Cookie string from browser
            
        Returns:
            True if authentication successful, False otherwise
        """
        self.logger.info("🍪 Setting up authentication with cookies...")
        
        # Parse cookies
        cookies = {}
        for cookie in cookie_string.split(';'):
            if '=' in cookie:
                name, value = cookie.strip().split('=', 1)
                cookies[name] = value
                self.session.cookies.set(name, value)
        
        self.cookies = cookies
        self.logger.info(f"✅ Set {len(cookies)} cookies")
        
        # Test authentication
        try:
            test_url = f"{self.base_url}/"
            response = self.session.get(test_url, timeout=30)
            
            if response.status_code == 200:
                if "login" not in response.text.lower() or "logout" in response.text.lower():
                    self.authenticated = True
                    self.logger.info("✅ Cookie authentication successful!")
                    return True
                else:
                    self.logger.error("❌ Cookie authentication failed - still showing login page")
                    return False
            else:
                self.logger.error(f"❌ Cookie authentication test failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Cookie authentication test error: {e}")
            return False
    
    def get_rss_feed(self, subcat_id: int, passkey: str) -> Optional[str]:
        """
        Fetch RSS feed content.
        
        Args:
            subcat_id: The subcategory ID (e.g., 2163 for Nintendo games)
            passkey: The passkey for authentication
            
        Returns:
            RSS feed content as string or None if failed
        """
        if not self.authenticated:
            self.logger.error("❌ Not authenticated. Please authenticate first.")
            return None
        
        rss_url = f"{self.base_url}/rss?action=generate&type=subcat&id={subcat_id}&passkey={passkey}"
        
        self.logger.info(f"📡 Fetching RSS feed: {rss_url}")
        
        try:
            response = self.session.get(rss_url, timeout=30)
            self.logger.info(f"📊 RSS response status: {response.status_code}")
            
            if response.status_code == 200:
                # Check if we got valid RSS content
                content_type = response.headers.get('content-type', '').lower()
                content = response.text.lower()
                
                if ('xml' in content_type or 'rss' in content_type or 
                    'rss' in content or 'xml' in content or 'item' in content):
                    self.logger.info("✅ Successfully fetched RSS feed")
                    return response.text
                else:
                    self.logger.warning("⚠ Response doesn't appear to be RSS content")
                    self.logger.warning(f"Content-Type: {response.headers.get('content-type')}")
                    
            elif response.status_code == 403:
                self.logger.error("❌ 403 Forbidden - authentication may have expired")
                self.authenticated = False
            else:
                self.logger.error(f"❌ Unexpected status code: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Request error: {e}")
        
        return None
    
    def parse_rss_feed(self, rss_content: str) -> List[Dict]:
        """Parse RSS feed content and extract torrent information."""
        torrents = []
        
        try:
            root = ET.fromstring(rss_content)
            
            # Handle different RSS namespaces
            namespaces = {
                'rss': 'http://purl.org/rss/1.0/',
                'atom': 'http://www.w3.org/2005/Atom',
                'dc': 'http://purl.org/dc/elements/1.1/',
                'torrent': 'http://xmlns.ezrss.it/0.1/'
            }
            
            # Find all items
            items = root.findall('.//item')
            if not items:
                items = root.findall('.//{http://purl.org/rss/1.0/}item')
            
            self.logger.info(f"📋 Found {len(items)} items in RSS feed")
            
            for item in items:
                torrent_info = self._extract_torrent_info(item, namespaces)
                if torrent_info:
                    torrents.append(torrent_info)
                    
        except ET.ParseError as e:
            self.logger.error(f"⚠ XML parsing error: {e}")
            torrents = self._parse_html_fallback(rss_content)
        
        return torrents
    
    def _extract_torrent_info(self, item, namespaces: Dict) -> Optional[Dict]:
        """Extract torrent information from an RSS item."""
        try:
            title = self._get_text(item, 'title')
            description = self._get_text(item, 'description')
            link = self._get_text(item, 'link')
            guid = self._get_text(item, 'guid')
            
            torrent_link = self._get_text(item, 'torrent:link', namespaces)
            torrent_info_hash = self._get_text(item, 'torrent:infoHash', namespaces)
            torrent_size = self._get_text(item, 'torrent:size', namespaces)
            torrent_seeds = self._get_text(item, 'torrent:seeds', namespaces)
            torrent_peers = self._get_text(item, 'torrent:peers', namespaces)
            
            pub_date = self._get_text(item, 'pubDate')
            category = self._get_text(item, 'category')
            
            torrent_info = {
                'title': title,
                'description': description,
                'link': link,
                'guid': guid,
                'torrent_link': torrent_link,
                'info_hash': torrent_info_hash,
                'size': torrent_size,
                'seeds': torrent_seeds,
                'peers': torrent_peers,
                'pub_date': pub_date,
                'category': category,
                'parsed_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return torrent_info
            
        except Exception as e:
            self.logger.error(f"⚠ Error extracting torrent info: {e}")
            return None
    
    def _get_text(self, element, tag: str, namespaces: Dict = None) -> Optional[str]:
        """Safely extract text from XML element."""
        try:
            if namespaces and ':' in tag:
                namespace, local_tag = tag.split(':', 1)
                if namespace in namespaces:
                    found = element.find(f'.//{{{namespaces[namespace]}}}{local_tag}')
                else:
                    found = element.find(f'.//{tag}')
            else:
                found = element.find(f'.//{tag}')
            
            return found.text.strip() if found is not None and found.text else None
        except:
            return None
    
    def _parse_html_fallback(self, content: str) -> List[Dict]:
        """Fallback parser for HTML content."""
        torrents = []
        try:
            soup = BeautifulSoup(content, 'html.parser')
            torrent_links = soup.find_all('a', href=re.compile(r'\.torrent$'))
            
            for link in torrent_links:
                torrent_info = {
                    'title': link.get_text(strip=True),
                    'torrent_link': urljoin(self.base_url, link.get('href', '')),
                    'parsed_at': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                torrents.append(torrent_info)
                
        except Exception as e:
            self.logger.error(f"⚠ Error in HTML fallback parsing: {e}")
        
        return torrents
    
    def get_torrent_file(self, torrent_url: str, save_path: str = None) -> Optional[bytes]:
        """Download a torrent file."""
        if not self.authenticated:
            self.logger.error("❌ Not authenticated. Please authenticate first.")
            return None
        
        try:
            response = self.session.get(torrent_url, timeout=30)
            response.raise_for_status()
            
            if save_path:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                self.logger.info(f"✅ Torrent saved to: {save_path}")
            
            return response.content
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Error downloading torrent file: {e}")
            return None
    
    def download_torrents_batch(self, torrents: List[Dict], max_workers: int = 3) -> Dict[str, str]:
        """
        Download multiple torrent files in parallel.
        
        Args:
            torrents: List of torrent dictionaries
            max_workers: Maximum number of concurrent downloads
            
        Returns:
            Dictionary mapping torrent titles to download paths
        """
        if not self.authenticated:
            self.logger.error("❌ Not authenticated. Please authenticate first.")
            return {}
        
        # Filter torrents that have torrent links
        downloadable_torrents = [t for t in torrents if t.get('torrent_link')]
        
        if not downloadable_torrents:
            self.logger.warning("⚠ No downloadable torrents found")
            return {}
        
        self.logger.info(f"🚀 Starting batch download of {len(downloadable_torrents)} torrents")
        
        results = {}
        
        def download_worker(torrent):
            """Worker function for downloading a single torrent."""
            title = torrent.get('title', 'Unknown')
            torrent_url = torrent['torrent_link']
            
            # Create safe filename
            safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)[:100]
            filename = f"{safe_title}.torrent"
            filepath = os.path.join(self.download_dir, filename)
            
            # Check if file already exists
            if os.path.exists(filepath):
                self.logger.info(f"📁 File already exists: {filepath}")
                return title, filepath
            
            try:
                response = self.session.get(torrent_url, timeout=30)
                response.raise_for_status()
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                self.logger.info(f"✅ Downloaded: {filepath}")
                return title, filepath
                
            except Exception as e:
                self.logger.error(f"❌ Error downloading {title}: {e}")
                return title, None
        
        # Download torrents in parallel
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_torrent = {
                executor.submit(download_worker, torrent): torrent 
                for torrent in downloadable_torrents
            }
            
            for future in as_completed(future_to_torrent):
                torrent = future_to_torrent[future]
                try:
                    title, filepath = future.result()
                    results[title] = filepath
                    
                except Exception as e:
                    title = torrent.get('title', 'Unknown')
                    self.logger.error(f"❌ Exception downloading {title}: {e}")
                    results[title] = None
        
        successful_downloads = sum(1 for path in results.values() if path)
        self.logger.info(f"🎉 Batch download completed: {successful_downloads}/{len(downloadable_torrents)} successful")
        
        return results
    
    def download_torrents_by_criteria(self, torrents: List[Dict], 
                                    min_seeds: int = 0, max_size_mb: int = None,
                                    keywords: List[str] = None) -> Dict[str, str]:
        """
        Download torrents based on specific criteria.
        
        Args:
            torrents: List of torrent dictionaries
            min_seeds: Minimum number of seeds required
            max_size_mb: Maximum size in MB
            keywords: List of keywords that must be in title
            
        Returns:
            Dictionary mapping torrent titles to download paths
        """
        def filter_func(torrent):
            # Check seeds
            seeds = torrent.get('seeds', '0')
            try:
                seeds = int(seeds)
                if seeds < min_seeds:
                    return False
            except (ValueError, TypeError):
                if min_seeds > 0:
                    return False
            
            # Check size
            if max_size_mb:
                size_str = torrent.get('size', '')
                size_mb = self._parse_size_to_mb(size_str)
                if size_mb and size_mb > max_size_mb:
                    return False
            
            # Check keywords
            if keywords:
                title = torrent.get('title', '').lower()
                if not any(keyword.lower() in title for keyword in keywords):
                    return False
            
            return True
        
        # Filter torrents
        filtered_torrents = [t for t in torrents if filter_func(t)]
        return self.download_torrents_batch(filtered_torrents)
    
    def _parse_size_to_mb(self, size_str: str) -> Optional[float]:
        """Parse size string to MB."""
        if not size_str:
            return None
        
        size_str = size_str.upper().strip()
        
        # Extract number and unit
        match = re.match(r'([\d.]+)\s*([KMGT]?B?)', size_str)
        if not match:
            return None
        
        number = float(match.group(1))
        unit = match.group(2)
        
        # Convert to MB
        if unit in ['B', '']:
            return number / (1024 * 1024)
        elif unit == 'KB':
            return number / 1024
        elif unit == 'MB':
            return number
        elif unit == 'GB':
            return number * 1024
        elif unit == 'TB':
            return number * 1024 * 1024
        
        return None
    
    def get_download_stats(self) -> Dict:
        """Get statistics about downloaded torrents."""
        if not os.path.exists(self.download_dir):
            return {'total_files': 0, 'total_size': 0, 'files': []}
        
        files = []
        total_size = 0
        
        for filename in os.listdir(self.download_dir):
            if filename.endswith('.torrent'):
                filepath = os.path.join(self.download_dir, filename)
                try:
                    size = os.path.getsize(filepath)
                    total_size += size
                    files.append({
                        'filename': filename,
                        'size': size,
                        'size_mb': size / (1024 * 1024),
                        'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                    })
                except OSError:
                    continue
        
        return {
            'total_files': len(files),
            'total_size': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'files': sorted(files, key=lambda x: x['modified'], reverse=True)
        }
    
    def save_torrents_to_json(self, torrents: List[Dict], filename: str = None) -> str:
        """Save torrent information to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"data/ygg_torrents_{timestamp}.json"
        
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(torrents, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"💾 Torrent information saved to: {filename}")
        return filename
    
    def get_available_categories(self) -> Dict[str, int]:
        """Return a dictionary of available subcategories."""
        return {
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


def main():
    """Main function for Ubuntu server deployment."""
    parser = YGGParserUbuntu()
    
    parser.logger.info("🚀 YGG Torrent Parser (Ubuntu Server)")
    parser.logger.info("=" * 50)
    
    # Try to load configuration
    try:
        from config_ubuntu import PASSKEY, SUBCATEGORIES
        parser.logger.info("✅ Loaded Ubuntu configuration")
    except ImportError:
        parser.logger.warning("⚠ No config_ubuntu.py found, using defaults")
        PASSKEY = "DJdLXYBi2WmyQB0PdNWZ8u9RZEnTqiXT"
        SUBCATEGORIES = parser.get_available_categories()
    
    # For server deployment, we'll use cookie-based authentication
    # In a real deployment, you would get these from environment variables or a secure config
    cookie_string = os.getenv('YGG_COOKIES', '')
    
    if not cookie_string:
        parser.logger.error("❌ No cookies provided. Set YGG_COOKIES environment variable.")
        parser.logger.info("💡 Example: export YGG_COOKIES='name1=value1; name2=value2'")
        return
    
    # Authenticate with cookies
    if not parser.authenticate_with_cookies(cookie_string):
        parser.logger.error("❌ Authentication failed")
        return
    
    # Process each category
    for category_name, subcat_id in SUBCATEGORIES.items():
        parser.logger.info(f"🔍 Processing {category_name} (ID: {subcat_id})...")
        
        # Fetch and parse RSS feed
        rss_content = parser.get_rss_feed(subcat_id, PASSKEY)
        
        if rss_content:
            torrents = parser.parse_rss_feed(rss_content)
            
            if torrents:
                parser.logger.info(f"✅ Found {len(torrents)} torrents in {category_name}")
                
                # Save to JSON
                filename = parser.save_torrents_to_json(torrents, f"data/{category_name.lower().replace(' ', '_')}_{int(time.time())}.json")
                
                # Log summary
                parser.logger.info(f"📊 {category_name} Summary:")
                for i, torrent in enumerate(torrents[:3], 1):
                    parser.logger.info(f"  {i}. {torrent.get('title', 'Unknown')}")
                
                if len(torrents) > 3:
                    parser.logger.info(f"  ... and {len(torrents) - 3} more torrents")
                
                # Download torrents based on environment variables
                download_enabled = os.getenv('YGG_DOWNLOAD_ENABLED', 'false').lower() == 'true'
                if download_enabled:
                    parser.logger.info(f"⬇️ Downloading torrents for {category_name}...")
                    
                    # Get download criteria from environment
                    min_seeds = int(os.getenv('YGG_MIN_SEEDS', '0'))
                    max_size_mb = int(os.getenv('YGG_MAX_SIZE_MB', '0')) or None
                    keywords_str = os.getenv('YGG_KEYWORDS', '')
                    keywords = [k.strip() for k in keywords_str.split(',')] if keywords_str else None
                    
                    # Download torrents
                    results = parser.download_torrents_by_criteria(
                        torrents, 
                        min_seeds=min_seeds, 
                        max_size_mb=max_size_mb, 
                        keywords=keywords
                    )
                    
                    successful = sum(1 for path in results.values() if path)
                    parser.logger.info(f"✅ Downloaded {successful} torrents for {category_name}")
            else:
                parser.logger.warning(f"⚠ No torrents found in {category_name}")
        else:
            parser.logger.error(f"❌ Failed to fetch RSS feed for {category_name}")
        
        # Small delay between categories
        time.sleep(2)
    
    parser.logger.info("🎉 Processing completed!")


if __name__ == "__main__":
    main()

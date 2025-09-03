#!/usr/bin/env python3
"""
YGG Torrent Parser with Enhanced Download Functionality
Includes batch downloading, progress tracking, and download management
"""

import requests
import xml.etree.ElementTree as ET
import json
import time
import re
import os
import logging
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional, Callable
from bs4 import BeautifulSoup
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False


class YGGParserWithDownloads:
    """YGG Torrent Parser with enhanced download functionality."""
    
    def __init__(self, base_url: str = "https://www.yggtorrent.top"):
        self.base_url = base_url
        self.session = None
        self.authenticated = False
        self.cookies = {}
        self.download_dir = "downloads"
        self.logger = self._setup_logging()
        self._setup_session()
        self._create_directories()
    
    def _setup_logging(self):
        """Setup logging for download tracking."""
        os.makedirs('logs', exist_ok=True)
        
        logger = logging.getLogger('ygg_parser_downloads')
        logger.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler('logs/downloads.log')
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
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
        
        # Set headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def _create_directories(self):
        """Create necessary directories."""
        os.makedirs(self.download_dir, exist_ok=True)
        os.makedirs('data', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
    
    def authenticate_with_cookies(self, cookie_string: str) -> bool:
        """Authenticate using cookie string from browser."""
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
        """Fetch RSS feed content."""
        if not self.authenticated:
            self.logger.error("❌ Not authenticated. Please authenticate first.")
            return None
        
        rss_url = f"{self.base_url}/rss?action=generate&type=subcat&id={subcat_id}&passkey={passkey}"
        
        self.logger.info(f"📡 Fetching RSS feed: {rss_url}")
        
        try:
            response = self.session.get(rss_url, timeout=30)
            self.logger.info(f"📊 RSS response status: {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                content = response.text.lower()
                
                if ('xml' in content_type or 'rss' in content_type or 
                    'rss' in content or 'xml' in content or 'item' in content):
                    self.logger.info("✅ Successfully fetched RSS feed")
                    return response.text
                else:
                    self.logger.warning("⚠ Response doesn't appear to be RSS content")
                    
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
            
            namespaces = {
                'rss': 'http://purl.org/rss/1.0/',
                'atom': 'http://www.w3.org/2005/Atom',
                'dc': 'http://purl.org/dc/elements/1.1/',
                'torrent': 'http://xmlns.ezrss.it/0.1/'
            }
            
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
                'parsed_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'downloaded': False,
                'download_path': None
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
                    'parsed_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'downloaded': False,
                    'download_path': None
                }
                torrents.append(torrent_info)
                
        except Exception as e:
            self.logger.error(f"⚠ Error in HTML fallback parsing: {e}")
        
        return torrents
    
    def download_torrent_file(self, torrent_url: str, filename: str = None, 
                            progress_callback: Callable = None) -> Optional[str]:
        """
        Download a single torrent file with progress tracking.
        
        Args:
            torrent_url: URL of the torrent file
            filename: Optional custom filename
            progress_callback: Optional callback for progress updates
            
        Returns:
            Path to downloaded file or None if failed
        """
        if not self.authenticated:
            self.logger.error("❌ Not authenticated. Please authenticate first.")
            return None
        
        try:
            # Generate filename if not provided
            if not filename:
                parsed_url = urlparse(torrent_url)
                filename = os.path.basename(parsed_url.path)
                if not filename or not filename.endswith('.torrent'):
                    filename = f"torrent_{int(time.time())}.torrent"
            
            # Ensure filename is safe
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            if not filename.endswith('.torrent'):
                filename += '.torrent'
            
            filepath = os.path.join(self.download_dir, filename)
            
            # Check if file already exists
            if os.path.exists(filepath):
                self.logger.info(f"📁 File already exists: {filepath}")
                return filepath
            
            self.logger.info(f"⬇️ Downloading: {filename}")
            
            # Download with progress tracking
            response = self.session.get(torrent_url, timeout=30, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Call progress callback if provided
                        if progress_callback and total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            progress_callback(filename, progress, downloaded_size, total_size)
            
            self.logger.info(f"✅ Downloaded: {filepath}")
            return filepath
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Error downloading torrent file: {e}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Unexpected error downloading torrent: {e}")
            return None
    
    def download_torrents_batch(self, torrents: List[Dict], max_workers: int = 3,
                              filter_func: Callable = None) -> Dict[str, str]:
        """
        Download multiple torrent files in parallel.
        
        Args:
            torrents: List of torrent dictionaries
            max_workers: Maximum number of concurrent downloads
            filter_func: Optional function to filter which torrents to download
            
        Returns:
            Dictionary mapping torrent titles to download paths
        """
        if not self.authenticated:
            self.logger.error("❌ Not authenticated. Please authenticate first.")
            return {}
        
        # Filter torrents if filter function provided
        if filter_func:
            torrents = [t for t in torrents if filter_func(t)]
        
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
            
            def progress_callback(name, progress, downloaded, total):
                if progress % 10 == 0:  # Log every 10%
                    self.logger.info(f"📊 {name}: {progress:.1f}% ({downloaded}/{total} bytes)")
            
            filepath = self.download_torrent_file(torrent_url, filename, progress_callback)
            
            if filepath:
                torrent['downloaded'] = True
                torrent['download_path'] = filepath
                return title, filepath
            else:
                return title, None
        
        # Download torrents in parallel
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
                    
                    if filepath:
                        self.logger.info(f"✅ Completed: {title}")
                    else:
                        self.logger.error(f"❌ Failed: {title}")
                        
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
        
        return self.download_torrents_batch(torrents, filter_func=filter_func)
    
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
            filename = f"data/ygg_torrents_with_downloads_{timestamp}.json"
        
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
    """Example usage of the YGG Parser with Downloads."""
    print("🚀 YGG Torrent Parser with Enhanced Downloads")
    print("=" * 50)
    
    parser = YGGParserWithDownloads()
    
    # Authentication
    cookie_string = input("Enter your YGG Torrent cookies: ").strip()
    if not cookie_string:
        print("❌ Cookies are required")
        return
    
    if not parser.authenticate_with_cookies(cookie_string):
        print("❌ Authentication failed")
        return
    
    # Get category
    categories = parser.get_available_categories()
    print("\n📂 Available categories:")
    for name, cat_id in categories.items():
        print(f"  {name}: {cat_id}")
    
    subcat_id = int(input("\nEnter subcategory ID: "))
    passkey = input("Enter your passkey: ").strip()
    
    if not passkey:
        print("❌ Passkey is required")
        return
    
    # Fetch and parse RSS feed
    print(f"\n🔍 Fetching torrents for subcategory {subcat_id}...")
    rss_content = parser.get_rss_feed(subcat_id, passkey)
    
    if not rss_content:
        print("❌ Failed to fetch RSS feed")
        return
    
    torrents = parser.parse_rss_feed(rss_content)
    
    if not torrents:
        print("❌ No torrents found")
        return
    
    print(f"✅ Found {len(torrents)} torrents")
    
    # Show first few torrents
    print("\n📋 First 5 torrents:")
    for i, torrent in enumerate(torrents[:5], 1):
        print(f"{i}. {torrent.get('title', 'Unknown')}")
        print(f"   📦 Size: {torrent.get('size', 'Unknown')}")
        print(f"   🌱 Seeds: {torrent.get('seeds', 'Unknown')}")
        print()
    
    # Download options
    print("\n📥 Download Options:")
    print("1. Download first torrent only")
    print("2. Download all torrents")
    print("3. Download torrents with criteria")
    print("4. Show download statistics")
    print("5. Exit")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        # Download first torrent
        if torrents[0].get('torrent_link'):
            print(f"\n⬇️ Downloading: {torrents[0].get('title')}")
            filepath = parser.download_torrent_file(torrents[0]['torrent_link'])
            if filepath:
                print(f"✅ Downloaded to: {filepath}")
            else:
                print("❌ Download failed")
    
    elif choice == "2":
        # Download all torrents
        confirm = input(f"\n⚠️ This will download {len(torrents)} torrents. Continue? (y/n): ")
        if confirm.lower() == 'y':
            results = parser.download_torrents_batch(torrents)
            successful = sum(1 for path in results.values() if path)
            print(f"✅ Downloaded {successful}/{len(torrents)} torrents")
    
    elif choice == "3":
        # Download with criteria
        print("\n🔍 Set download criteria:")
        min_seeds = int(input("Minimum seeds (0 for any): ") or "0")
        max_size = input("Maximum size in MB (empty for no limit): ").strip()
        max_size = int(max_size) if max_size else None
        keywords = input("Keywords (comma-separated, empty for any): ").strip()
        keywords = [k.strip() for k in keywords.split(',')] if keywords else None
        
        results = parser.download_torrents_by_criteria(
            torrents, min_seeds=min_seeds, max_size_mb=max_size, keywords=keywords
        )
        successful = sum(1 for path in results.values() if path)
        print(f"✅ Downloaded {successful} torrents matching criteria")
    
    elif choice == "4":
        # Show statistics
        stats = parser.get_download_stats()
        print(f"\n📊 Download Statistics:")
        print(f"Total files: {stats['total_files']}")
        print(f"Total size: {stats['total_size_mb']:.2f} MB")
        print(f"Recent files:")
        for file_info in stats['files'][:5]:
            print(f"  {file_info['filename']} ({file_info['size_mb']:.2f} MB)")
    
    # Save torrent information
    json_file = parser.save_torrents_to_json(torrents)
    print(f"\n💾 Torrent information saved to: {json_file}")
    
    print("\n🎉 Done!")


if __name__ == "__main__":
    main()

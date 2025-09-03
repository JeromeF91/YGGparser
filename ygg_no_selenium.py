#!/usr/bin/env python3
"""
YGG Torrent Parser without Selenium
Uses alternative methods to bypass Cloudflare and access the RSS feed
"""

import os
import json
import time
import requests
import cloudscraper
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET


def setup_session():
    """Setup a session with cloudscraper and realistic headers."""
    session = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'linux',
            'mobile': False
        }
    )
    
    # Set realistic headers
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    })
    
    return session


def test_direct_access():
    """Test direct access to YGG Torrent without authentication."""
    print("🧪 Testing direct access to YGG Torrent...")
    
    session = setup_session()
    
    try:
        # Try to access the main page
        response = session.get("https://www.yggtorrent.top", timeout=30)
        print(f"📊 Main page status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Successfully accessed main page!")
            return session
        else:
            print(f"❌ Failed to access main page: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error accessing main page: {e}")
        return None


def test_rss_access(session):
    """Test RSS feed access."""
    print("\n🧪 Testing RSS feed access...")
    
    # RSS URL
    rss_url = "https://www.yggtorrent.top/rss?action=generate&type=subcat&id=2163&passkey=DJdLXYBi2WmyQB0PdNWZ8u9RZEnTqiXT"
    
    try:
        response = session.get(rss_url, timeout=30)
        print(f"📊 RSS feed status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Successfully accessed RSS feed!")
            
            # Check if it's valid XML
            if response.text.strip().startswith('<?xml'):
                print("✅ Valid XML RSS feed received!")
                return response.text
            else:
                print("⚠️ Response doesn't look like valid XML")
                print(f"📄 First 200 characters: {response.text[:200]}")
                return None
        else:
            print(f"❌ Failed to access RSS feed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error accessing RSS feed: {e}")
        return None


def parse_rss_content(rss_content):
    """Parse RSS content and extract torrent information."""
    if not rss_content:
        return None
    
    print("\n📋 Parsing RSS content...")
    
    try:
        root = ET.fromstring(rss_content)
        
        # Find all items
        items = root.findall('.//item')
        print(f"✅ Found {len(items)} torrents in RSS feed")
        
        torrents = []
        for item in items[:10]:  # Show first 10
            title = item.find('title')
            link = item.find('link')
            description = item.find('description')
            pub_date = item.find('pubDate')
            
            if title is not None:
                torrent_info = {
                    'title': title.text,
                    'link': link.text if link is not None else None,
                    'description': description.text if description is not None else None,
                    'pub_date': pub_date.text if pub_date is not None else None
                }
                torrents.append(torrent_info)
                print(f"📄 {title.text}")
        
        return torrents
        
    except Exception as e:
        print(f"❌ Error parsing RSS: {e}")
        return None


def try_alternative_methods():
    """Try alternative methods to access the RSS feed."""
    print("\n🔧 Trying alternative methods...")
    
    # Method 1: Different user agent
    print("\n🔧 Method 1: Different user agent...")
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/rss+xml, application/xml, text/xml, */*',
        'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Referer': 'https://www.yggtorrent.top/',
    })
    
    rss_url = "https://www.yggtorrent.top/rss?action=generate&type=subcat&id=2163&passkey=DJdLXYBi2WmyQB0PdNWZ8u9RZEnTqiXT"
    
    try:
        response = session.get(rss_url, timeout=30)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200 and response.text.strip().startswith('<?xml'):
            print("✅ Success with different user agent!")
            return response.text
        else:
            print(f"❌ Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Method 2: With delays and session establishment
    print("\n🔧 Method 2: With session establishment...")
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/rss+xml, application/xml, text/xml, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
    })
    
    try:
        # First, get the main page
        print("📄 Getting main page first...")
        main_response = session.get("https://www.yggtorrent.top", timeout=30)
        print(f"📊 Main page status: {main_response.status_code}")
        
        time.sleep(2)
        
        # Then get RSS
        print("📡 Getting RSS feed...")
        response = session.get(rss_url, timeout=30)
        print(f"📊 RSS status: {response.status_code}")
        
        if response.status_code == 200 and response.text.strip().startswith('<?xml'):
            print("✅ Success with session establishment!")
            return response.text
        else:
            print(f"❌ Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Method 3: Using requests-html (if available)
    print("\n🔧 Method 3: Using requests-html...")
    try:
        from requests_html import HTMLSession
        
        session = HTMLSession()
        response = session.get(rss_url, timeout=30)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200 and response.text.strip().startswith('<?xml'):
            print("✅ Success with requests-html!")
            return response.text
        else:
            print(f"❌ Failed: {response.status_code}")
            
    except ImportError:
        print("❌ requests-html not available")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n❌ All alternative methods failed")
    return None


def save_results(rss_content, torrents, method):
    """Save results to files."""
    if not rss_content:
        return
    
    os.makedirs('data', exist_ok=True)
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    
    # Save RSS content
    rss_file = f"data/rss_content_{method}_{timestamp}.xml"
    with open(rss_file, 'w', encoding='utf-8') as f:
        f.write(rss_content)
    print(f"💾 RSS content saved to: {rss_file}")
    
    # Save parsed torrents
    if torrents:
        torrents_file = f"data/torrents_{method}_{timestamp}.json"
        with open(torrents_file, 'w', encoding='utf-8') as f:
            json.dump(torrents, f, indent=2, ensure_ascii=False)
        print(f"💾 Torrents data saved to: {torrents_file}")
    
    return rss_file, torrents_file if torrents else None


def main():
    """Main function."""
    print("🚀 YGG Torrent Parser without Selenium")
    print("=" * 50)
    print("This script tries to access YGG Torrent RSS feed without using Selenium.")
    print("=" * 50)
    
    # Test direct access
    session = test_direct_access()
    
    if session:
        # Test RSS access
        rss_content = test_rss_access(session)
        
        if rss_content:
            # Parse content
            torrents = parse_rss_content(rss_content)
            
            # Save results
            save_results(rss_content, torrents, "direct")
            
            print("\n🎉 Successfully accessed RSS feed!")
            print(f"✅ Found {len(torrents) if torrents else 0} torrents")
            
        else:
            print("\n⚠️ Direct access failed, trying alternative methods...")
            
            # Try alternative methods
            rss_content = try_alternative_methods()
            
            if rss_content:
                # Parse content
                torrents = parse_rss_content(rss_content)
                
                # Save results
                save_results(rss_content, torrents, "alternative")
                
                print("\n🎉 Successfully accessed RSS feed with alternative method!")
                print(f"✅ Found {len(torrents) if torrents else 0} torrents")
            else:
                print("\n❌ All methods failed")
                print("\n💡 Suggestions:")
                print("  1. The passkey might be invalid or expired")
                print("  2. Try using a VPN")
                print("  3. Try from a different network")
                print("  4. Check if the RSS feed URL is correct")
    else:
        print("\n❌ Could not access YGG Torrent")
        print("\n💡 Suggestions:")
        print("  1. Check your internet connection")
        print("  2. Try using a VPN")
        print("  3. The site might be temporarily unavailable")
    
    print("\n📁 Check the 'data/' directory for saved files")


if __name__ == "__main__":
    main()

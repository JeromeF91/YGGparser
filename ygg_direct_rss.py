#!/usr/bin/env python3
"""
Direct RSS Feed Access for YGG Torrent
Tries different methods to access the RSS feed directly
"""

import requests
import cloudscraper
import time
import json
import os
from urllib.parse import urljoin


def test_direct_rss_access():
    """Test direct RSS feed access with different methods."""
    print("🍪 YGG Torrent Direct RSS Access")
    print("=" * 50)
    print("This script tries different methods to access the RSS feed directly.")
    print("=" * 50)
    
    # RSS URL
    rss_url = "https://www.yggtorrent.top/rss?action=generate&type=subcat&id=2163&passkey=DJdLXYBi2WmyQB0PdNWZ8u9RZEnTqiXT"
    
    print(f"📡 RSS URL: {rss_url}")
    
    # Method 1: Standard requests
    print("\n🔧 Method 1: Standard requests...")
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
        })
        
        response = session.get(rss_url, timeout=30)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success with standard requests!")
            return response.text, "standard_requests"
        else:
            print(f"❌ Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Method 2: Cloudscraper
    print("\n🔧 Method 2: Cloudscraper...")
    try:
        session = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'linux',
                'mobile': False
            }
        )
        
        response = session.get(rss_url, timeout=30)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success with cloudscraper!")
            return response.text, "cloudscraper"
        else:
            print(f"❌ Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Method 3: Different User Agent
    print("\n🔧 Method 3: Different User Agent...")
    try:
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
        
        response = session.get(rss_url, timeout=30)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success with different User Agent!")
            return response.text, "different_ua"
        else:
            print(f"❌ Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Method 4: With delays
    print("\n🔧 Method 4: With delays...")
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
        })
        
        # First, get the main page
        print("📄 Getting main page first...")
        main_response = session.get("https://www.yggtorrent.top", timeout=30)
        print(f"📊 Main page status: {main_response.status_code}")
        
        time.sleep(2)
        
        # Then get RSS
        print("📡 Getting RSS feed...")
        response = session.get(rss_url, timeout=30)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success with delays!")
            return response.text, "with_delays"
        else:
            print(f"❌ Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n❌ All methods failed")
    return None, None


def parse_rss_content(rss_content):
    """Parse RSS content and extract torrent information."""
    if not rss_content:
        return None
    
    print("\n📋 Parsing RSS content...")
    
    # Check if it's valid XML
    if not rss_content.strip().startswith('<?xml'):
        print("⚠️ Content doesn't look like valid XML")
        print(f"📄 First 200 characters: {rss_content[:200]}")
        return None
    
    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(rss_content)
        
        # Find all items
        items = root.findall('.//item')
        print(f"✅ Found {len(items)} torrents in RSS feed")
        
        torrents = []
        for item in items[:5]:  # Show first 5
            title = item.find('title')
            link = item.find('link')
            description = item.find('description')
            
            if title is not None:
                torrent_info = {
                    'title': title.text,
                    'link': link.text if link is not None else None,
                    'description': description.text if description is not None else None
                }
                torrents.append(torrent_info)
                print(f"📄 {title.text}")
        
        return torrents
        
    except Exception as e:
        print(f"❌ Error parsing RSS: {e}")
        return None


def save_rss_content(rss_content, method):
    """Save RSS content to file."""
    if not rss_content:
        return
    
    os.makedirs('data', exist_ok=True)
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    filename = f"data/rss_content_{method}_{timestamp}.xml"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(rss_content)
    
    print(f"💾 RSS content saved to: {filename}")
    return filename


def main():
    """Main function."""
    try:
        rss_content, method = test_direct_rss_access()
        
        if rss_content:
            print(f"\n🎉 Successfully accessed RSS feed using method: {method}")
            
            # Save content
            filename = save_rss_content(rss_content, method)
            
            # Parse content
            torrents = parse_rss_content(rss_content)
            
            if torrents:
                print(f"\n✅ Successfully parsed {len(torrents)} torrents")
                
                # Save parsed data
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                torrents_file = f"data/torrents_{method}_{timestamp}.json"
                
                with open(torrents_file, 'w', encoding='utf-8') as f:
                    json.dump(torrents, f, indent=2, ensure_ascii=False)
                
                print(f"💾 Torrents data saved to: {torrents_file}")
                
                print("\n🚀 You can now use this method in your parser!")
            else:
                print("\n⚠️ Could not parse torrents from RSS content")
        else:
            print("\n❌ Could not access RSS feed with any method")
            print("\n💡 Suggestions:")
            print("  1. Try using a VPN")
            print("  2. Try from a different network")
            print("  3. Check if the passkey is still valid")
            print("  4. Try the manual cookie method")
            
    except KeyboardInterrupt:
        print("\n⏹️ RSS access interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n📁 Check the 'data/' directory for saved files")


if __name__ == "__main__":
    main()

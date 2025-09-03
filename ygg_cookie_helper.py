#!/usr/bin/env python3
"""
YGG Torrent Cookie Helper
Helps you get cookies from your browser and test them
"""

import os
import json
import time
import requests
import cloudscraper
from urllib.parse import urljoin


def get_cookies_from_browser():
    """Guide user to get cookies from their browser."""
    print("🍪 YGG Torrent Cookie Helper")
    print("=" * 50)
    print("This tool helps you get cookies from your browser and test them.")
    print("\n📋 HOW TO GET COOKIES FROM YOUR BROWSER:")
    print("1. Open your regular browser (Chrome, Firefox, Safari)")
    print("2. Go to https://www.yggtorrent.top")
    print("3. Complete any Cloudflare challenges manually")
    print("4. Login with your credentials (JF16v / torrent123)")
    print("5. Press F12 to open Developer Tools")
    print("6. Go to Application/Storage tab → Cookies → https://www.yggtorrent.top")
    print("7. Copy the cookie values")
    print("=" * 50)
    
    # Get cookie string from user
    print("\n🍪 Enter the cookie string from your browser:")
    print("(It should look like: ygg_uid=123; ygg_passkey=abc; session=xyz)")
    cookie_string = input("Cookie string: ").strip()
    
    if not cookie_string:
        print("❌ Cookie string is required")
        return None
    
    # Parse cookies
    cookies = {}
    for cookie in cookie_string.split(';'):
        if '=' in cookie:
            name, value = cookie.strip().split('=', 1)
            cookies[name] = value
    
    if not cookies:
        print("❌ No valid cookies found in the string")
        return None
    
    print(f"✅ Parsed {len(cookies)} cookies")
    return cookies


def test_cookies(cookies):
    """Test if the cookies work."""
    print("\n🧪 Testing cookies...")
    
    # Create session with cloudscraper
    session = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'linux',
            'mobile': False
        }
    )
    
    # Set cookies
    for name, value in cookies.items():
        session.cookies.set(name, value)
    
    # Test with main page
    try:
        response = session.get("https://www.yggtorrent.top", timeout=30)
        print(f"📊 Main page status: {response.status_code}")
        
        if response.status_code == 200:
            page_content = response.text.lower()
            
            if 'logout' in page_content or 'déconnexion' in page_content:
                print("✅ Cookies are working! You appear to be logged in.")
                return True
            else:
                print("⚠️ Cookies might not be working - no login indicators found")
                return False
        else:
            print(f"❌ Main page access failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing cookies: {e}")
        return False


def test_rss_access(cookies):
    """Test RSS feed access with cookies."""
    print("\n🧪 Testing RSS feed access...")
    
    # Create session
    session = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'linux',
            'mobile': False
        }
    )
    
    # Set cookies
    for name, value in cookies.items():
        session.cookies.set(name, value)
    
    # Test RSS feed
    rss_url = "https://www.yggtorrent.top/rss?action=generate&type=subcat&id=2163&passkey=DJdLXYBi2WmyQB0PdNWZ8u9RZEnTqiXT"
    
    try:
        response = session.get(rss_url, timeout=30)
        print(f"📊 RSS feed status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ RSS feed access successful!")
            print(f"📄 RSS content length: {len(response.text)} characters")
            
            # Check if it's valid XML
            if response.text.strip().startswith('<?xml'):
                print("✅ Valid XML RSS feed received!")
                return response.text
            else:
                print("⚠️ Response doesn't look like valid XML")
                print(f"📄 First 200 characters: {response.text[:200]}")
                return None
        else:
            print(f"❌ RSS feed access failed: {response.status_code}")
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
        import xml.etree.ElementTree as ET
        root = ET.fromstring(rss_content)
        
        # Find all items
        items = root.findall('.//item')
        print(f"✅ Found {len(items)} torrents in RSS feed")
        
        torrents = []
        for item in items[:10]:  # Show first 10
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


def save_results(cookies, rss_content, torrents):
    """Save results to files."""
    os.makedirs('data', exist_ok=True)
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    
    # Save cookies
    cookie_file = f"data/working_cookies_{timestamp}.json"
    with open(cookie_file, 'w') as f:
        json.dump(cookies, f, indent=2)
    print(f"💾 Cookies saved to: {cookie_file}")
    
    # Save RSS content
    if rss_content:
        rss_file = f"data/working_rss_{timestamp}.xml"
        with open(rss_file, 'w', encoding='utf-8') as f:
            f.write(rss_content)
        print(f"💾 RSS content saved to: {rss_file}")
    
    # Save parsed torrents
    if torrents:
        torrents_file = f"data/working_torrents_{timestamp}.json"
        with open(torrents_file, 'w', encoding='utf-8') as f:
            json.dump(torrents, f, indent=2, ensure_ascii=False)
        print(f"💾 Torrents data saved to: {torrents_file}")
    
    # Create cookie string
    cookie_string = '; '.join([f"{name}={value}" for name, value in cookies.items()])
    print(f"🍪 Cookie string: {cookie_string}")
    
    return cookie_file, cookie_string


def main():
    """Main function."""
    try:
        # Get cookies from user
        cookies = get_cookies_from_browser()
        
        if not cookies:
            print("❌ No cookies provided")
            return
        
        # Test cookies
        if test_cookies(cookies):
            print("✅ Cookie test passed!")
            
            # Test RSS access
            rss_content = test_rss_access(cookies)
            
            if rss_content:
                print("✅ RSS feed access successful!")
                
                # Parse content
                torrents = parse_rss_content(rss_content)
                
                if torrents:
                    print(f"✅ Successfully parsed {len(torrents)} torrents")
                    
                    # Save results
                    cookie_file, cookie_string = save_results(cookies, rss_content, torrents)
                    
                    print("\n🎉 Everything is working! You can now use the parser.")
                    print("\n🚀 Next steps:")
                    print("  1. Use the cookie string in your parser scripts")
                    print("  2. Run: python3 ygg_parser.py")
                    print("  3. Or test with: python3 ygg_downloader.py")
                    print(f"\n📋 Cookie string: {cookie_string}")
                else:
                    print("⚠️ Could not parse torrents from RSS content")
            else:
                print("❌ RSS feed access failed")
                print("\n💡 The cookies might not have the right permissions for RSS access")
        else:
            print("❌ Cookie test failed")
            print("\n💡 Please check your cookies and try again")
            
    except KeyboardInterrupt:
        print("\n⏹️ Cookie helper interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n📁 Check the 'data/' directory for saved files")


if __name__ == "__main__":
    main()

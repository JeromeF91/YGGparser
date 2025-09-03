#!/usr/bin/env python3
"""
Manual Cookie Input for YGG Torrent
Get cookies from your regular browser and input them manually
"""

import os
import json
import time
import requests
import cloudscraper
from urllib.parse import urljoin


def get_cookies_manually():
    """Get cookies by manual input from user's browser."""
    print("🍪 YGG Torrent Manual Cookie Input")
    print("=" * 50)
    print("This method avoids Cloudflare by using cookies from your regular browser.")
    print("\n📋 HOW TO GET COOKIES:")
    print("1. Open your regular browser (Chrome, Firefox, Safari)")
    print("2. Go to https://www.yggtorrent.top")
    print("3. Complete any Cloudflare challenges manually")
    print("4. Login with your credentials (JF16v / torrent123)")
    print("5. Press F12 to open Developer Tools")
    print("6. Go to Application/Storage tab → Cookies → https://www.yggtorrent.top")
    print("7. Copy the cookie values")
    print("=" * 50)
    
    # Get credentials
    print("\n🔐 Enter your YGG Torrent credentials:")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    
    if not username or not password:
        print("❌ Username and password are required")
        return None
    
    print(f"\n🔐 Credentials: {username}")
    
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
    
    # Test the cookies
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
    
    # Test with a simple request
    try:
        response = session.get("https://www.yggtorrent.top", timeout=30)
        
        if response.status_code == 200:
            page_content = response.text.lower()
            
            # Check for login indicators
            if 'logout' in page_content or 'déconnexion' in page_content:
                print("✅ Cookies are working! You appear to be logged in.")
            else:
                print("⚠️ Cookies might not be working - no login indicators found")
                choice = input("❓ Do you want to continue anyway? (y/N): ").strip().lower()
                if choice != 'y':
                    return None
        else:
            print(f"⚠️ Got status code {response.status_code}")
            choice = input("❓ Do you want to continue anyway? (y/N): ").strip().lower()
            if choice != 'y':
                return None
                
    except Exception as e:
        print(f"⚠️ Error testing cookies: {e}")
        choice = input("❓ Do you want to continue anyway? (y/N): ").strip().lower()
        if choice != 'y':
            return None
    
    # Save cookies
    os.makedirs('data', exist_ok=True)
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    cookie_file = f"data/manual_input_cookies_{timestamp}.json"
    
    with open(cookie_file, 'w') as f:
        json.dump(cookies, f, indent=2)
    
    print(f"\n💾 Cookies saved to: {cookie_file}")
    
    # Create config file
    config = {
        "cookies": cookies,
        "cookie_string": cookie_string,
        "username": username,
        "extracted_at": time.strftime('%Y-%m-%d %H:%M:%S'),
        "base_url": "https://www.yggtorrent.top"
    }
    
    config_file = f"data/manual_input_config_{timestamp}.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"⚙️ Configuration saved to: {config_file}")
    
    print("\n🎉 Manual cookie input completed!")
    print("\n📋 You can now use these cookies in other scripts:")
    print(f"  Cookie string: {cookie_string}")
    print(f"  Config file: {config_file}")
    
    return cookie_string


def test_rss_with_cookies(cookie_string):
    """Test RSS feed access with the cookies."""
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
    for cookie in cookie_string.split(';'):
        if '=' in cookie:
            name, value = cookie.strip().split('=', 1)
            session.cookies.set(name, value)
    
    # Test RSS feed
    rss_url = "https://www.yggtorrent.top/rss?action=generate&type=subcat&id=2163&passkey=DJdLXYBi2WmyQB0PdNWZ8u9RZEnTqiXT"
    
    try:
        response = session.get(rss_url, timeout=30)
        
        if response.status_code == 200:
            print("✅ RSS feed access successful!")
            print(f"📄 RSS content length: {len(response.text)} characters")
            
            # Check if it's valid XML
            if response.text.strip().startswith('<?xml'):
                print("✅ Valid XML RSS feed received!")
                return True
            else:
                print("⚠️ Response doesn't look like valid XML")
                print(f"📄 First 200 characters: {response.text[:200]}")
                return False
        else:
            print(f"❌ RSS feed access failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error accessing RSS feed: {e}")
        return False


def main():
    """Main function."""
    try:
        cookie_string = get_cookies_manually()
        
        if cookie_string:
            print("\n✅ Manual cookie input completed successfully!")
            
            # Test RSS access
            if test_rss_with_cookies(cookie_string):
                print("\n🎉 Everything is working! You can now use the parser.")
                print("\n🚀 Next steps:")
                print("  1. Run: python3 ygg_parser.py")
                print("  2. Or test with: python3 ygg_downloader.py")
            else:
                print("\n⚠️ RSS feed access failed. The cookies might not be valid.")
                print("Please try getting fresh cookies from your browser.")
        else:
            print("\n❌ Manual cookie input failed")
            
    except KeyboardInterrupt:
        print("\n⏹️ Cookie input interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n📁 Check the 'data/' directory for saved files")


if __name__ == "__main__":
    main()

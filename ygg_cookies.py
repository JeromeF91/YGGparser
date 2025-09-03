#!/usr/bin/env python3
"""
Simple script to get real YGG Torrent cookies
Run this to authenticate and extract real cookies for use in other scripts
"""

import os
import json
import time
from ygg_auth import YGGRealAuth


def get_real_cookies():
    """Get real cookies from YGG Torrent."""
    print("🍪 YGG Torrent Real Cookie Extractor")
    print("=" * 40)
    
    # Initialize authentication system
    auth = YGGRealAuth()
    
    # Get credentials
    print("🔐 Enter your YGG Torrent credentials:")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    
    if not username or not password:
        print("❌ Username and password are required")
        return None
    
    print(f"\n🔐 Authenticating user: {username}")
    
    # Try Selenium authentication first
    print("\n🌐 Attempting Selenium authentication...")
    success, cookies = auth.authenticate_with_selenium(username, password, headless=False)
    
    if not success:
        print("❌ Selenium authentication failed, trying requests method...")
        success, cookies = auth.authenticate_with_requests(username, password)
    
    if not success:
        print("❌ Authentication failed")
        print("💡 Possible reasons:")
        print("  - Invalid username/password")
        print("  - Account locked or suspended")
        print("  - Cloudflare protection")
        print("  - Network issues")
        return None
    
    print("✅ Authentication successful!")
    print(f"🍪 Extracted {len(cookies)} cookies")
    
    # Test authentication
    print("\n🧪 Testing authentication...")
    if not auth.test_authentication():
        print("❌ Authentication test failed")
        return None
    
    print("✅ Authentication test passed!")
    
    # Save cookies
    cookie_file = auth.save_cookies()
    cookie_string = auth.get_cookie_string()
    
    print(f"\n💾 Cookies saved to: {cookie_file}")
    print(f"🍪 Cookie string: {cookie_string}")
    
    # Create a simple config file for easy use
    config = {
        "cookies": cookies,
        "cookie_string": cookie_string,
        "username": username,
        "authenticated_at": time.strftime('%Y-%m-%d %H:%M:%S'),
        "base_url": "https://www.yggtorrent.top"
    }
    
    config_file = "data/ygg_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"⚙️ Configuration saved to: {config_file}")
    
    print("\n🎉 Real cookies extracted successfully!")
    print("\n📋 You can now use these cookies in other scripts:")
    print(f"  Cookie string: {cookie_string}")
    print(f"  Config file: {config_file}")
    
    return cookie_string


def main():
    """Main function."""
    try:
        cookie_string = get_real_cookies()
        
        if cookie_string:
            print("\n✅ Cookie extraction completed successfully!")
            print("\n🚀 Next steps:")
            print("  1. Use the cookie string in your parser scripts")
            print("  2. Run: python3 ygg_parser_with_downloads.py")
            print("  3. Or test with: python3 test_real_auth_download.py")
        else:
            print("\n❌ Cookie extraction failed")
            
    except KeyboardInterrupt:
        print("\n⏹️ Cookie extraction interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n📁 Check the 'data/' directory for saved files")


if __name__ == "__main__":
    main()

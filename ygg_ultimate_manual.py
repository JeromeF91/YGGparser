#!/usr/bin/env python3
"""
Ultimate Manual YGG Torrent Cookie Extractor
Complete manual control - you handle everything, script just extracts cookies
"""

import os
import json
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException


def setup_logging():
    """Setup logging."""
    os.makedirs('logs', exist_ok=True)
    
    logger = logging.getLogger('ygg_ultimate_manual')
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger


def get_cookies_ultimate_manual():
    """Get cookies with ultimate manual control."""
    logger = setup_logging()
    
    print("🍪 YGG Torrent Ultimate Manual Cookie Extractor")
    print("=" * 70)
    print("This script gives you COMPLETE control:")
    print("1. Opens browser to YGG Torrent")
    print("2. You handle ALL Cloudflare challenges manually")
    print("3. You login manually")
    print("4. You navigate wherever you want")
    print("5. Script extracts cookies when YOU decide")
    print("=" * 70)
    
    driver = None
    
    try:
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Create driver
        logger.info("🚀 Opening browser...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Navigate to YGG Torrent
        logger.info("📄 Navigating to YGG Torrent...")
        driver.get("https://www.yggtorrent.top")
        
        print("\n" + "="*70)
        print("🌐 BROWSER WINDOW IS NOW OPEN")
        print("="*70)
        print("The browser window is open at YGG Torrent.")
        print("\n📋 STEP-BY-STEP INSTRUCTIONS:")
        print("1. 🛡️  Complete any Cloudflare challenges (click checkboxes, solve CAPTCHAs)")
        print("2. 🔐 Go to login page and login with your credentials")
        print("3. 🏠 Navigate to the homepage or any page you want")
        print("4. ✅ Make sure you can see you're logged in (logout button, profile, etc.)")
        print("5. ⏸️  Come back here and press ENTER when ready")
        print("\n⚠️  IMPORTANT: Only press ENTER when you're fully logged in!")
        print("   Don't press ENTER while still on Cloudflare pages!")
        print("="*70)
        
        # Wait for user to complete everything
        input("\n👤 Press ENTER ONLY when you are fully logged in and ready to extract cookies...")
        
        # Get current page info
        current_url = driver.current_url
        page_title = driver.title or "Unknown"
        page_source = driver.page_source.lower()
        
        print(f"\n📄 Current URL: {current_url}")
        print(f"📄 Page title: {page_title}")
        
        # Check if still on Cloudflare
        cloudflare_indicators = ["just a moment", "checking your browser", "cloudflare"]
        is_cloudflare = any(indicator in page_title.lower() or indicator in page_source for indicator in cloudflare_indicators)
        
        if is_cloudflare:
            print("\n⚠️  WARNING: You appear to still be on a Cloudflare page!")
            print("The page title contains: 'Just a moment...' or similar")
            print("This means the cookies won't be valid for accessing the site.")
            
            choice = input("\n❓ Do you want to continue anyway? (y/N): ").strip().lower()
            if choice != 'y':
                print("🔄 Please complete the Cloudflare challenge and login, then run this script again.")
                return None
        
        # Check if logged in
        login_indicators = ['logout', 'déconnexion', 'profile', 'profil', 'account', 'compte']
        has_login_indicators = any(indicator in page_source for indicator in login_indicators)
        
        if not has_login_indicators:
            print("\n⚠️  WARNING: No login indicators found on the page!")
            print("This might mean you're not logged in yet.")
            
            choice = input("\n❓ Do you want to continue anyway? (y/N): ").strip().lower()
            if choice != 'y':
                print("🔄 Please login first, then run this script again.")
                return None
        
        # Extract cookies
        logger.info("🍪 Extracting cookies...")
        selenium_cookies = driver.get_cookies()
        cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
        
        if not cookies:
            print("❌ No cookies found! This shouldn't happen.")
            return None
        
        print(f"✅ Extracted {len(cookies)} cookies")
        
        # Show cookie info
        print("\n🍪 Cookie details:")
        for name, value in list(cookies.items())[:10]:  # Show first 10 cookies
            print(f"  {name}: {value[:50]}...")
        if len(cookies) > 10:
            print(f"  ... and {len(cookies) - 10} more cookies")
        
        # Check for important cookies
        important_cookies = ['ygg_passkey', 'ygg_uid', 'ygg_session', 'passkey', 'uid', 'session']
        found_important = [name for name in cookies.keys() if any(important in name.lower() for important in important_cookies)]
        
        if found_important:
            print(f"\n✅ Found important cookies: {found_important}")
        else:
            print("\n⚠️  No obvious login cookies found. This might not work for accessing protected content.")
        
        # Save cookies
        os.makedirs('data', exist_ok=True)
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        cookie_file = f"data/ultimate_cookies_{timestamp}.json"
        
        with open(cookie_file, 'w') as f:
            json.dump(cookies, f, indent=2)
        
        print(f"\n💾 Cookies saved to: {cookie_file}")
        
        # Create cookie string
        cookie_string = '; '.join([f"{name}={value}" for name, value in cookies.items()])
        print(f"🍪 Cookie string: {cookie_string}")
        
        # Create config file
        config = {
            "cookies": cookies,
            "cookie_string": cookie_string,
            "extracted_at": time.strftime('%Y-%m-%d %H:%M:%S'),
            "url": current_url,
            "title": page_title,
            "is_logged_in": has_login_indicators,
            "important_cookies": found_important,
            "base_url": "https://www.yggtorrent.top"
        }
        
        config_file = f"data/ultimate_config_{timestamp}.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"⚙️ Configuration saved to: {config_file}")
        
        print("\n🎉 Ultimate manual cookie extraction completed!")
        print("\n📋 You can now use these cookies in other scripts:")
        print(f"  Cookie string: {cookie_string}")
        print(f"  Config file: {config_file}")
        
        return cookie_string
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        print(f"\n❌ Error: {e}")
        return None
        
    finally:
        if driver:
            print("\n🔒 Closing browser...")
            driver.quit()


def main():
    """Main function."""
    try:
        cookie_string = get_cookies_ultimate_manual()
        
        if cookie_string:
            print("\n✅ Ultimate manual cookie extraction completed successfully!")
            print("\n🚀 Next steps:")
            print("  1. Use the cookie string in your parser scripts")
            print("  2. Run: python3 ygg_parser.py")
            print("  3. Or test with: python3 ygg_downloader.py")
        else:
            print("\n❌ Ultimate manual cookie extraction failed")
            
    except KeyboardInterrupt:
        print("\n⏹️ Cookie extraction interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n📁 Check the 'data/' directory for saved files")


if __name__ == "__main__":
    main()

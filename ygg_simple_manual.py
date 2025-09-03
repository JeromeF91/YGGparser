#!/usr/bin/env python3
"""
Simple Manual YGG Torrent Cookie Extractor
Opens browser, lets you manually login, then extracts cookies
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
    
    logger = logging.getLogger('ygg_simple_manual')
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger


def get_cookies_manually():
    """Get cookies by opening browser and letting user manually login."""
    logger = setup_logging()
    
    print("🍪 YGG Torrent Simple Manual Cookie Extractor")
    print("=" * 60)
    print("This will open a browser window where you can:")
    print("1. Complete any Cloudflare challenges manually")
    print("2. Login to YGG Torrent manually")
    print("3. Navigate to any page you want")
    print("4. Press ENTER when ready to extract cookies")
    print("=" * 60)
    
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
        
        print("\n" + "="*60)
        print("🌐 BROWSER WINDOW OPENED")
        print("="*60)
        print("The browser window is now open at YGG Torrent.")
        print("\nPlease:")
        print("1. Complete any Cloudflare challenges that appear")
        print("2. Login to your account manually")
        print("3. Navigate to any page you want (homepage, profile, etc.)")
        print("4. Make sure you're logged in and can see your account")
        print("\nWhen you're ready to extract the cookies, come back here and press ENTER.")
        print("="*60)
        
        # Wait for user to complete manual login
        input("\n👤 Press ENTER when you have completed login and are ready to extract cookies...")
        
        # Get current page info
        current_url = driver.current_url
        page_title = driver.title or "Unknown"
        
        print(f"\n📄 Current URL: {current_url}")
        print(f"📄 Page title: {page_title}")
        
        # Extract cookies
        logger.info("🍪 Extracting cookies...")
        selenium_cookies = driver.get_cookies()
        cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
        
        if not cookies:
            print("❌ No cookies found! Make sure you're logged in.")
            return None
        
        print(f"✅ Extracted {len(cookies)} cookies")
        
        # Show some cookie info
        print("\n🍪 Cookie details:")
        for name, value in list(cookies.items())[:5]:  # Show first 5 cookies
            print(f"  {name}: {value[:50]}...")
        if len(cookies) > 5:
            print(f"  ... and {len(cookies) - 5} more cookies")
        
        # Save cookies
        os.makedirs('data', exist_ok=True)
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        cookie_file = f"data/manual_cookies_{timestamp}.json"
        
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
            "base_url": "https://www.yggtorrent.top"
        }
        
        config_file = f"data/manual_config_{timestamp}.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"⚙️ Configuration saved to: {config_file}")
        
        print("\n🎉 Manual cookie extraction completed successfully!")
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
        cookie_string = get_cookies_manually()
        
        if cookie_string:
            print("\n✅ Manual cookie extraction completed successfully!")
            print("\n🚀 Next steps:")
            print("  1. Use the cookie string in your parser scripts")
            print("  2. Run: python3 ygg_parser.py")
            print("  3. Or test with: python3 ygg_downloader.py")
        else:
            print("\n❌ Manual cookie extraction failed")
            
    except KeyboardInterrupt:
        print("\n⏹️ Cookie extraction interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n📁 Check the 'data/' directory for saved files")


if __name__ == "__main__":
    main()

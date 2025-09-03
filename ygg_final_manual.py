#!/usr/bin/env python3
"""
Final Manual YGG Torrent Cookie Extractor
Keeps browser open, gives you full control, extracts cookies when ready
"""

import os
import json
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException


def setup_logging():
    """Setup logging."""
    os.makedirs('logs', exist_ok=True)
    
    logger = logging.getLogger('ygg_final_manual')
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger


def create_stealth_browser():
    """Create a stealth browser that avoids Cloudflare detection."""
    logger = setup_logging()
    
    print("🕵️ Creating Stealth Browser for YGG Torrent")
    print("=" * 60)
    print("This browser uses advanced stealth techniques:")
    print("- Realistic browser fingerprint")
    print("- Human-like behavior simulation")
    print("- Cloudflare bypass techniques")
    print("- Keeps browser open for manual control")
    print("=" * 60)
    
    # Setup Chrome options for maximum stealth
    chrome_options = Options()
    
    # Basic options
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-plugins')
    
    # Advanced stealth options
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-features=VizDisplayCompositor,TranslateUI')
    chrome_options.add_argument('--disable-ipc-flooding-protection')
    chrome_options.add_argument('--disable-renderer-backgrounding')
    chrome_options.add_argument('--disable-backgrounding-occluded-windows')
    chrome_options.add_argument('--disable-client-side-phishing-detection')
    chrome_options.add_argument('--disable-sync')
    chrome_options.add_argument('--disable-default-apps')
    chrome_options.add_argument('--disable-hang-monitor')
    chrome_options.add_argument('--disable-prompt-on-repost')
    chrome_options.add_argument('--disable-domain-reliability')
    chrome_options.add_argument('--disable-component-extensions-with-background-pages')
    
    # User agent and window size
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    chrome_options.add_argument('--window-size=1366,768')
    
    # Experimental options
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("detach", True)  # Keep browser open
    
    # Create driver
    logger.info("🚀 Creating stealth browser...")
    driver = webdriver.Chrome(options=chrome_options)
    
    # Execute stealth scripts
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
    
    return driver, logger


def stealth_navigation(driver, logger):
    """Navigate to YGG Torrent with stealth techniques."""
    logger.info("🌐 Navigating to YGG Torrent with stealth techniques...")
    
    # First, go to a neutral page to establish session
    logger.info("📄 Going to Google first to establish session...")
    driver.get("https://www.google.com")
    time.sleep(3)
    
    # Simulate human behavior
    actions = ActionChains(driver)
    actions.move_by_offset(100, 100).perform()
    time.sleep(1)
    
    # Now navigate to YGG Torrent
    logger.info("📄 Navigating to YGG Torrent...")
    driver.get("https://www.yggtorrent.top")
    
    # Wait and simulate human behavior
    time.sleep(3)
    actions.move_by_offset(200, 200).perform()
    time.sleep(1)
    
    return driver


def get_cookies_final_manual():
    """Get cookies with final manual approach."""
    driver = None
    
    try:
        driver, logger = create_stealth_browser()
        
        # Navigate with stealth techniques
        driver = stealth_navigation(driver, logger)
        
        print("\n" + "="*70)
        print("🕵️ STEALTH BROWSER IS NOW OPEN")
        print("="*70)
        print("The browser is configured with advanced stealth techniques.")
        print("It should automatically bypass Cloudflare challenges.")
        print("\n📋 WHAT TO DO NOW:")
        print("1. 🛡️  Wait for any Cloudflare challenges to complete automatically")
        print("2. 🔐 Navigate to the login page: https://www.yggtorrent.top/auth/login")
        print("3. 🔑 Login with your credentials (JF16v / torrent123)")
        print("4. 🏠 Navigate to the homepage or any page you want")
        print("5. ✅ Make sure you can see you're logged in")
        print("6. ⏸️  Come back here and press ENTER when ready")
        print("\n⚠️  The browser will stay open - take your time!")
        print("="*70)
        
        # Wait for user to complete everything
        input("\n👤 Press ENTER when you have completed login and are ready to extract cookies...")
        
        # Get current page info
        current_url = driver.current_url
        page_title = driver.title or "Unknown"
        page_source = driver.page_source.lower()
        
        print(f"\n📄 Current URL: {current_url}")
        print(f"📄 Page title: {page_title}")
        
        # Check if logged in
        login_indicators = ['logout', 'déconnexion', 'profile', 'profil', 'account', 'compte']
        has_login_indicators = any(indicator in page_source for indicator in login_indicators)
        
        if has_login_indicators:
            print("✅ Login indicators found - you appear to be logged in!")
        else:
            print("⚠️ No login indicators found - you might not be logged in yet")
            choice = input("\n❓ Do you want to continue anyway? (y/N): ").strip().lower()
            if choice != 'y':
                print("🔄 Please login first, then run this script again.")
                return None
        
        # Extract cookies
        logger.info("🍪 Extracting cookies...")
        selenium_cookies = driver.get_cookies()
        cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
        
        if not cookies:
            print("❌ No cookies found!")
            return None
        
        print(f"✅ Extracted {len(cookies)} cookies")
        
        # Show cookie info
        print("\n🍪 Cookie details:")
        for name, value in list(cookies.items())[:10]:
            print(f"  {name}: {value[:50]}...")
        if len(cookies) > 10:
            print(f"  ... and {len(cookies) - 10} more cookies")
        
        # Check for important cookies
        important_cookies = ['ygg_passkey', 'ygg_uid', 'ygg_session', 'passkey', 'uid', 'session']
        found_important = [name for name in cookies.keys() if any(important in name.lower() for important in important_cookies)]
        
        if found_important:
            print(f"\n✅ Found important cookies: {found_important}")
        else:
            print("\n⚠️ No obvious login cookies found")
        
        # Save cookies
        os.makedirs('data', exist_ok=True)
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        cookie_file = f"data/final_cookies_{timestamp}.json"
        
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
        
        config_file = f"data/final_config_{timestamp}.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"⚙️ Configuration saved to: {config_file}")
        
        print("\n🎉 Final manual cookie extraction completed!")
        print("\n📋 You can now use these cookies in other scripts:")
        print(f"  Cookie string: {cookie_string}")
        print(f"  Config file: {config_file}")
        
        # Ask if user wants to keep browser open
        keep_open = input("\n❓ Do you want to keep the browser open? (y/N): ").strip().lower()
        if keep_open == 'y':
            print("🌐 Browser will stay open. Close it manually when done.")
            return cookie_string
        else:
            driver.quit()
            return cookie_string
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None
        
    finally:
        # Only close if not keeping open
        if driver and not input("\n❓ Keep browser open? (y/N): ").strip().lower() == 'y':
            print("\n🔒 Closing browser...")
            driver.quit()


def main():
    """Main function."""
    try:
        cookie_string = get_cookies_final_manual()
        
        if cookie_string:
            print("\n✅ Final manual cookie extraction completed successfully!")
            print("\n🚀 Next steps:")
            print("  1. Use the cookie string in your parser scripts")
            print("  2. Run: python3 ygg_parser.py")
            print("  3. Or test with: python3 ygg_downloader.py")
        else:
            print("\n❌ Final manual cookie extraction failed")
            
    except KeyboardInterrupt:
        print("\n⏹️ Cookie extraction interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n📁 Check the 'data/' directory for saved files")


if __name__ == "__main__":
    main()

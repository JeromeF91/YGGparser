#!/usr/bin/env python3
"""
Human-like Browser for YGG Torrent
Uses stealth techniques to avoid Cloudflare detection
"""

import os
import json
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException


def setup_logging():
    """Setup logging."""
    os.makedirs('logs', exist_ok=True)
    
    logger = logging.getLogger('ygg_human_browser')
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger


def create_human_like_browser():
    """Create a browser that looks more human-like to avoid Cloudflare detection."""
    logger = setup_logging()
    
    print("🤖 Creating Human-like Browser for YGG Torrent")
    print("=" * 60)
    print("This browser is configured to avoid Cloudflare detection:")
    print("- Uses realistic browser fingerprint")
    print("- Simulates human-like behavior")
    print("- Includes random delays")
    print("- Uses stealth techniques")
    print("=" * 60)
    
    # Setup Chrome options for maximum stealth
    chrome_options = Options()
    
    # Basic stealth options
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-plugins')
    chrome_options.add_argument('--disable-images')  # Faster loading
    chrome_options.add_argument('--disable-javascript')  # Disable JS to avoid some detection
    
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
    chrome_options.add_argument('--disable-background-timer-throttling')
    chrome_options.add_argument('--disable-backgrounding-occluded-windows')
    chrome_options.add_argument('--disable-renderer-backgrounding')
    
    # User agent and window size
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    chrome_options.add_argument('--window-size=1366,768')
    
    # Experimental options
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("detach", True)
    
    # Create driver
    logger.info("🚀 Creating human-like browser...")
    driver = webdriver.Chrome(options=chrome_options)
    
    # Execute stealth scripts
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
    
    return driver, logger


def human_like_navigation(driver, logger):
    """Navigate to YGG Torrent with human-like behavior."""
    logger.info("🌐 Navigating to YGG Torrent with human-like behavior...")
    
    # First, go to a neutral page to establish session
    logger.info("📄 Going to Google first to establish session...")
    driver.get("https://www.google.com")
    time.sleep(2)
    
    # Simulate human behavior - move mouse around
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


def wait_for_cloudflare_completion(driver, logger, max_wait_time=120):
    """Wait for Cloudflare challenge to complete with human-like behavior."""
    logger.info("⏳ Waiting for Cloudflare challenge to complete...")
    
    start_time = time.time()
    last_title = ""
    
    while time.time() - start_time < max_wait_time:
        try:
            current_title = driver.title or ""
            current_url = driver.current_url
            
            # Check if we're still on Cloudflare
            cloudflare_indicators = [
                "just a moment",
                "checking your browser",
                "please wait",
                "ddos protection",
                "cloudflare"
            ]
            
            is_cloudflare = any(indicator in current_title.lower() for indicator in cloudflare_indicators)
            
            if not is_cloudflare and current_title != last_title:
                logger.info(f"✅ Cloudflare challenge completed! Title: {current_title}")
                return True
            
            if current_title != last_title:
                logger.info(f"📄 Page title changed: {current_title}")
                last_title = current_title
            
            # Simulate human behavior - random mouse movements
            actions = ActionChains(driver)
            import random
            actions.move_by_offset(random.randint(-50, 50), random.randint(-50, 50)).perform()
            
            time.sleep(2)
            
        except Exception as e:
            logger.warning(f"⚠️ Error checking page status: {e}")
            time.sleep(2)
    
    logger.warning("⚠️ Cloudflare challenge timeout")
    return False


def get_cookies_human_like():
    """Get cookies using human-like browser behavior."""
    driver = None
    
    try:
        driver, logger = create_human_like_browser()
        
        # Navigate with human-like behavior
        driver = human_like_navigation(driver, logger)
        
        print("\n" + "="*60)
        print("🌐 HUMAN-LIKE BROWSER IS NOW OPEN")
        print("="*60)
        print("The browser is configured to avoid Cloudflare detection.")
        print("\n📋 WHAT TO DO:")
        print("1. 🛡️  If you see Cloudflare challenges, wait for them to complete automatically")
        print("2. 🔐 Navigate to the login page manually")
        print("3. 🔑 Login with your credentials")
        print("4. 🏠 Go to the homepage or any page")
        print("5. ⏸️  Come back here and press ENTER when ready")
        print("\n⚠️  The browser will try to handle Cloudflare automatically")
        print("="*60)
        
        # Wait for Cloudflare to complete automatically
        if wait_for_cloudflare_completion(driver, logger):
            print("✅ Cloudflare challenge completed automatically!")
        else:
            print("⚠️ Cloudflare challenge may need manual intervention")
        
        # Wait for user to complete login
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
        cookie_file = f"data/human_cookies_{timestamp}.json"
        
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
        
        config_file = f"data/human_config_{timestamp}.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"⚙️ Configuration saved to: {config_file}")
        
        print("\n🎉 Human-like cookie extraction completed!")
        print("\n📋 You can now use these cookies in other scripts:")
        print(f"  Cookie string: {cookie_string}")
        print(f"  Config file: {config_file}")
        
        return cookie_string
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None
        
    finally:
        if driver:
            print("\n🔒 Closing browser...")
            driver.quit()


def main():
    """Main function."""
    try:
        cookie_string = get_cookies_human_like()
        
        if cookie_string:
            print("\n✅ Human-like cookie extraction completed successfully!")
            print("\n🚀 Next steps:")
            print("  1. Use the cookie string in your parser scripts")
            print("  2. Run: python3 ygg_parser.py")
            print("  3. Or test with: python3 ygg_downloader.py")
        else:
            print("\n❌ Human-like cookie extraction failed")
            
    except KeyboardInterrupt:
        print("\n⏹️ Cookie extraction interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n📁 Check the 'data/' directory for saved files")


if __name__ == "__main__":
    main()

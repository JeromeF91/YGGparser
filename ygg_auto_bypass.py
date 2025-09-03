#!/usr/bin/env python3
"""
Automatic YGG Torrent Cookie Extractor with Cloudflare Bypass
Uses advanced techniques to automatically bypass Cloudflare and get cookies
"""

import os
import json
import time
import logging
import requests
import cloudscraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import random


def setup_logging():
    """Setup logging."""
    os.makedirs('logs', exist_ok=True)
    
    logger = logging.getLogger('ygg_auto_bypass')
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger


class YGGAutoBypass:
    """Automatic YGG Torrent authentication with Cloudflare bypass."""
    
    def __init__(self):
        self.logger = setup_logging()
        self.driver = None
        self.cookies = {}
        self.session = None
    
    def create_stealth_driver(self):
        """Create a stealth Chrome driver that avoids detection."""
        self.logger.info("🕵️ Creating stealth Chrome driver...")
        
        chrome_options = Options()
        
        # Basic options
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-images')  # Faster loading
        
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
        chrome_options.add_argument('--disable-features=TranslateUI')
        chrome_options.add_argument('--disable-ipc-flooding-protection')
        
        # User agent and window size
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--window-size=1366,768')
        
        # Experimental options
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option("detach", True)
        
        # Create driver
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # Execute stealth scripts
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
        self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
        self.driver.execute_script("Object.defineProperty(navigator, 'platform', {get: () => 'MacIntel'})")
        
        return self.driver
    
    def human_like_behavior(self):
        """Simulate human-like behavior."""
        actions = ActionChains(self.driver)
        
        # Random mouse movements
        for _ in range(3):
            x_offset = random.randint(-100, 100)
            y_offset = random.randint(-100, 100)
            actions.move_by_offset(x_offset, y_offset).perform()
            time.sleep(random.uniform(0.5, 1.5))
        
        # Random scroll
        scroll_amount = random.randint(-300, 300)
        self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        time.sleep(random.uniform(0.5, 1.0))
    
    def bypass_cloudflare_automatically(self):
        """Automatically bypass Cloudflare challenge."""
        self.logger.info("🛡️ Attempting to bypass Cloudflare automatically...")
        
        # Wait for page to load
        time.sleep(3)
        
        # Check for Cloudflare challenge
        cloudflare_indicators = [
            "just a moment",
            "checking your browser",
            "please wait",
            "ddos protection",
            "cloudflare",
            "cf-browser-verification"
        ]
        
        max_attempts = 10
        attempt = 0
        
        while attempt < max_attempts:
            try:
                page_source = self.driver.page_source.lower()
                title = (self.driver.title or "").lower()
                
                is_cloudflare = any(indicator in page_source or indicator in title for indicator in cloudflare_indicators)
                
                if is_cloudflare:
                    self.logger.info(f"⏳ Cloudflare challenge detected (attempt {attempt + 1}/{max_attempts})...")
                    
                    # Simulate human behavior
                    self.human_like_behavior()
                    
                    # Wait for challenge to complete
                    time.sleep(random.uniform(5, 10))
                    
                    # Check if challenge completed
                    new_page_source = self.driver.page_source.lower()
                    new_title = (self.driver.title or "").lower()
                    still_cloudflare = any(indicator in new_page_source or indicator in new_title for indicator in cloudflare_indicators)
                    
                    if not still_cloudflare:
                        self.logger.info("✅ Cloudflare challenge completed automatically!")
                        return True
                    
                    attempt += 1
                else:
                    self.logger.info("✅ No Cloudflare challenge detected")
                    return True
                    
            except Exception as e:
                self.logger.warning(f"⚠️ Error checking Cloudflare status: {e}")
                attempt += 1
                time.sleep(2)
        
        self.logger.warning("⚠️ Could not automatically bypass Cloudflare")
        return False
    
    def navigate_to_login(self):
        """Navigate to login page."""
        self.logger.info("📄 Navigating to login page...")
        
        # First, go to a neutral page
        self.driver.get("https://www.google.com")
        time.sleep(2)
        
        # Simulate human behavior
        self.human_like_behavior()
        
        # Navigate to YGG Torrent
        self.driver.get("https://www.yggtorrent.top")
        time.sleep(3)
        
        # Try to bypass Cloudflare
        if not self.bypass_cloudflare_automatically():
            self.logger.warning("⚠️ Cloudflare bypass failed, continuing anyway...")
        
        # Navigate to login page
        login_url = "https://www.yggtorrent.top/auth/login"
        self.driver.get(login_url)
        time.sleep(3)
        
        # Try to bypass Cloudflare again
        self.bypass_cloudflare_automatically()
        
        return True
    
    def find_and_fill_form(self, username, password):
        """Find and fill the login form."""
        self.logger.info("🔍 Looking for login form...")
        
        # Wait for form to load
        time.sleep(2)
        
        # Try to find username field
        username_field = None
        username_selectors = [
            "input[name='id']",
            "input[name='username']", 
            "input[name='user']",
            "input[name='login']",
            "input[type='text']",
            "input[type='email']",
            "#id",
            "#username",
            "#user",
            "#login"
        ]
        
        for selector in username_selectors:
            try:
                username_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                self.logger.info(f"✅ Found username field with selector: {selector}")
                break
            except NoSuchElementException:
                continue
        
        if not username_field:
            # Try to find any text input
            try:
                text_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
                if text_inputs:
                    username_field = text_inputs[0]
                    self.logger.info("✅ Found username field (first text input)")
            except:
                pass
        
        if not username_field:
            self.logger.error("❌ Could not find username field")
            return False
        
        # Try to find password field
        password_field = None
        password_selectors = [
            "input[name='pass']",
            "input[name='password']",
            "input[name='pwd']",
            "input[type='password']",
            "#pass",
            "#password",
            "#pwd"
        ]
        
        for selector in password_selectors:
            try:
                password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                self.logger.info(f"✅ Found password field with selector: {selector}")
                break
            except NoSuchElementException:
                continue
        
        if not password_field:
            # Try to find any password input
            try:
                password_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
                if password_inputs:
                    password_field = password_inputs[0]
                    self.logger.info("✅ Found password field (first password input)")
            except:
                pass
        
        if not password_field:
            self.logger.error("❌ Could not find password field")
            return False
        
        # Fill form with human-like behavior
        self.logger.info("📝 Filling login form...")
        
        # Clear and type username
        username_field.clear()
        for char in username:
            username_field.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
        
        # Simulate human behavior
        self.human_like_behavior()
        
        # Clear and type password
        password_field.clear()
        for char in password:
            password_field.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
        
        return True
    
    def submit_form(self):
        """Submit the login form."""
        self.logger.info("🚀 Submitting login form...")
        
        # Find submit button
        submit_button = None
        submit_selectors = [
            "input[type='submit']",
            "button[type='submit']",
            "input[value='Connexion']",
            "input[value='Login']",
            "input[value='Se connecter']",
            ".submit",
            ".login-button",
            "#submit",
            "#login-button"
        ]
        
        for selector in submit_selectors:
            try:
                submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                self.logger.info(f"✅ Found submit button with selector: {selector}")
                break
            except NoSuchElementException:
                continue
        
        if not submit_button:
            # Try to find any button that might be submit
            try:
                buttons = self.driver.find_elements(By.CSS_SELECTOR, "button, input[type='submit']")
                for button in buttons:
                    button_text = button.get_attribute('value') or button.text or ''
                    if any(word in button_text.lower() for word in ['login', 'connexion', 'connecter', 'submit']):
                        submit_button = button
                        self.logger.info(f"✅ Found submit button by text: {button_text}")
                        break
            except:
                pass
        
        if not submit_button:
            self.logger.error("❌ Could not find submit button")
            return False
        
        # Click submit button
        submit_button.click()
        
        # Wait for login to process
        time.sleep(5)
        
        return True
    
    def check_login_success(self):
        """Check if login was successful."""
        self.logger.info("🧪 Checking login success...")
        
        current_url = self.driver.current_url
        page_source = self.driver.page_source.lower()
        
        self.logger.info(f"📄 Current URL: {current_url}")
        self.logger.info(f"📄 Page title: {self.driver.title}")
        
        # Check for success indicators
        success_indicators = ['logout', 'déconnexion', 'profile', 'profil', 'account', 'compte', 'dashboard']
        failure_indicators = ['login', 'connexion', 'error', 'erreur', 'invalid', 'incorrect']
        
        has_success = any(indicator in page_source for indicator in success_indicators)
        has_failure = any(indicator in page_source for indicator in failure_indicators)
        
        if has_success and not has_failure:
            self.logger.info("✅ Login successful!")
            return True
        else:
            self.logger.error("❌ Login failed")
            return False
    
    def extract_cookies(self):
        """Extract cookies from the browser."""
        self.logger.info("🍪 Extracting cookies...")
        
        selenium_cookies = self.driver.get_cookies()
        self.cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
        
        self.logger.info(f"✅ Extracted {len(self.cookies)} cookies")
        
        # Show cookie info
        for name, value in list(self.cookies.items())[:5]:
            self.logger.info(f"  {name}: {value[:50]}...")
        
        return self.cookies
    
    def authenticate_automatically(self, username, password):
        """Automatically authenticate with YGG Torrent."""
        try:
            self.logger.info("🚀 Starting automatic authentication...")
            
            # Create stealth driver
            self.create_stealth_driver()
            
            # Navigate to login
            self.navigate_to_login()
            
            # Find and fill form
            if not self.find_and_fill_form(username, password):
                return False, {}
            
            # Submit form
            if not self.submit_form():
                return False, {}
            
            # Check login success
            if not self.check_login_success():
                return False, {}
            
            # Extract cookies
            cookies = self.extract_cookies()
            
            return True, cookies
            
        except Exception as e:
            self.logger.error(f"❌ Authentication error: {e}")
            return False, {}
        finally:
            if self.driver:
                self.driver.quit()
    
    def test_cookies(self):
        """Test if the extracted cookies work."""
        self.logger.info("🧪 Testing extracted cookies...")
        
        # Create session with cloudscraper
        self.session = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'linux',
                'mobile': False
            }
        )
        
        # Set cookies
        for name, value in self.cookies.items():
            self.session.cookies.set(name, value)
        
        # Test with a simple request
        try:
            response = self.session.get("https://www.yggtorrent.top", timeout=30)
            
            if response.status_code == 200:
                page_content = response.text.lower()
                
                if 'logout' in page_content or 'déconnexion' in page_content:
                    self.logger.info("✅ Cookie test successful!")
                    return True
                else:
                    self.logger.warning("⚠️ Cookie test failed - no login indicators")
                    return False
            else:
                self.logger.error(f"❌ Cookie test failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Cookie test error: {e}")
            return False
    
    def save_cookies(self):
        """Save cookies to file."""
        os.makedirs('data', exist_ok=True)
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        cookie_file = f"data/auto_cookies_{timestamp}.json"
        
        with open(cookie_file, 'w') as f:
            json.dump(self.cookies, f, indent=2)
        
        self.logger.info(f"💾 Cookies saved to: {cookie_file}")
        return cookie_file
    
    def get_cookie_string(self):
        """Get cookies as a string format."""
        return '; '.join([f"{name}={value}" for name, value in self.cookies.items()])


def main():
    """Main function."""
    print("🤖 YGG Torrent Automatic Cookie Extractor")
    print("=" * 50)
    print("This script automatically bypasses Cloudflare and extracts cookies.")
    print("=" * 50)
    
    # Get credentials
    username = input("Enter YGG Torrent username: ").strip()
    password = input("Enter YGG Torrent password: ").strip()
    
    if not username or not password:
        print("❌ Username and password are required")
        return
    
    # Create authenticator
    auth = YGGAutoBypass()
    
    # Authenticate automatically
    success, cookies = auth.authenticate_automatically(username, password)
    
    if success:
        print("✅ Automatic authentication successful!")
        print(f"🍪 Extracted {len(cookies)} cookies")
        
        # Test cookies
        if auth.test_cookies():
            print("✅ Cookie test passed!")
            
            # Save cookies
            cookie_file = auth.save_cookies()
            cookie_string = auth.get_cookie_string()
            
            print(f"\n💾 Cookies saved to: {cookie_file}")
            print(f"🍪 Cookie string: {cookie_string}")
            
            print("\n🎉 Automatic cookie extraction completed successfully!")
            print("\n🚀 Next steps:")
            print("  1. Use the cookie string in your parser scripts")
            print("  2. Run: python3 ygg_parser.py")
            print("  3. Or test with: python3 ygg_downloader.py")
        else:
            print("❌ Cookie test failed")
    else:
        print("❌ Automatic authentication failed")
        print("\n💡 Suggestions:")
        print("  1. Check your credentials")
        print("  2. Try again later")
        print("  3. Use the manual cookie method")


if __name__ == "__main__":
    main()

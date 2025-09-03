#!/usr/bin/env python3
"""
Simple Automatic YGG Torrent Cookie Extractor
Simplified approach that focuses on reliability over complexity
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


def setup_logging():
    """Setup logging."""
    os.makedirs('logs', exist_ok=True)
    
    logger = logging.getLogger('ygg_simple_auto')
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger


class YGGSimpleAuto:
    """Simple automatic YGG Torrent authentication."""
    
    def __init__(self):
        self.logger = setup_logging()
        self.driver = None
        self.cookies = {}
    
    def create_driver(self):
        """Create a simple Chrome driver."""
        self.logger.info("🚀 Creating Chrome driver...")
        
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--window-size=1366,768')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return self.driver
    
    def wait_for_cloudflare(self, max_wait=60):
        """Wait for Cloudflare challenge to complete."""
        self.logger.info("⏳ Waiting for Cloudflare challenge...")
        
        start_time = time.time()
        last_title = ""
        
        while time.time() - start_time < max_wait:
            try:
                current_title = self.driver.title or ""
                
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
                    self.logger.info(f"✅ Cloudflare challenge completed! Title: {current_title}")
                    return True
                
                if current_title != last_title:
                    self.logger.info(f"📄 Page title: {current_title}")
                    last_title = current_title
                
                time.sleep(2)
                
            except Exception as e:
                self.logger.warning(f"⚠️ Error checking page status: {e}")
                time.sleep(2)
        
        self.logger.warning("⚠️ Cloudflare challenge timeout")
        return False
    
    def navigate_to_login(self):
        """Navigate to login page."""
        self.logger.info("📄 Navigating to login page...")
        
        # Go directly to login page
        login_url = "https://www.yggtorrent.top/auth/login"
        self.driver.get(login_url)
        
        # Wait for Cloudflare
        self.wait_for_cloudflare()
        
        return True
    
    def find_form_fields(self):
        """Find username and password fields."""
        self.logger.info("🔍 Looking for form fields...")
        
        # Wait for form to load
        time.sleep(3)
        
        # Find username field
        username_field = None
        username_selectors = [
            "input[name='id']",
            "input[name='username']", 
            "input[name='user']",
            "input[type='text']",
            "#id",
            "#username"
        ]
        
        for selector in username_selectors:
            try:
                username_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                self.logger.info(f"✅ Found username field: {selector}")
                break
            except NoSuchElementException:
                continue
        
        if not username_field:
            self.logger.error("❌ Could not find username field")
            return None, None
        
        # Find password field
        password_field = None
        password_selectors = [
            "input[name='pass']",
            "input[name='password']",
            "input[type='password']",
            "#pass",
            "#password"
        ]
        
        for selector in password_selectors:
            try:
                password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                self.logger.info(f"✅ Found password field: {selector}")
                break
            except NoSuchElementException:
                continue
        
        if not password_field:
            self.logger.error("❌ Could not find password field")
            return None, None
        
        return username_field, password_field
    
    def fill_form(self, username_field, password_field, username, password):
        """Fill the login form."""
        self.logger.info("📝 Filling login form...")
        
        # Clear and fill username
        username_field.clear()
        username_field.send_keys(username)
        
        # Clear and fill password
        password_field.clear()
        password_field.send_keys(password)
        
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
            ".submit",
            "#submit"
        ]
        
        for selector in submit_selectors:
            try:
                submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                self.logger.info(f"✅ Found submit button: {selector}")
                break
            except NoSuchElementException:
                continue
        
        if not submit_button:
            self.logger.error("❌ Could not find submit button")
            return False
        
        # Click submit
        submit_button.click()
        
        # Wait for login
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
        success_indicators = ['logout', 'déconnexion', 'profile', 'profil', 'account', 'compte']
        has_success = any(indicator in page_source for indicator in success_indicators)
        
        if has_success:
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
        
        return self.cookies
    
    def authenticate(self, username, password):
        """Main authentication method."""
        try:
            self.logger.info("🚀 Starting authentication...")
            
            # Create driver
            self.create_driver()
            
            # Navigate to login
            self.navigate_to_login()
            
            # Find form fields
            username_field, password_field = self.find_form_fields()
            if not username_field or not password_field:
                return False, {}
            
            # Fill form
            self.fill_form(username_field, password_field, username, password)
            
            # Submit form
            self.submit_form()
            
            # Check success
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
        self.logger.info("🧪 Testing cookies...")
        
        # Create session
        session = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'linux',
                'mobile': False
            }
        )
        
        # Set cookies
        for name, value in self.cookies.items():
            session.cookies.set(name, value)
        
        # Test request
        try:
            response = session.get("https://www.yggtorrent.top", timeout=30)
            
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
        cookie_file = f"data/simple_auto_cookies_{timestamp}.json"
        
        with open(cookie_file, 'w') as f:
            json.dump(self.cookies, f, indent=2)
        
        self.logger.info(f"💾 Cookies saved to: {cookie_file}")
        return cookie_file
    
    def get_cookie_string(self):
        """Get cookies as a string format."""
        return '; '.join([f"{name}={value}" for name, value in self.cookies.items()])


def main():
    """Main function."""
    print("🤖 YGG Torrent Simple Automatic Cookie Extractor")
    print("=" * 60)
    print("This script automatically extracts cookies from YGG Torrent.")
    print("=" * 60)
    
    # Get credentials
    username = input("Enter YGG Torrent username: ").strip()
    password = input("Enter YGG Torrent password: ").strip()
    
    if not username or not password:
        print("❌ Username and password are required")
        return
    
    # Create authenticator
    auth = YGGSimpleAuto()
    
    # Authenticate
    success, cookies = auth.authenticate(username, password)
    
    if success:
        print("✅ Authentication successful!")
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
        print("❌ Authentication failed")
        print("\n💡 Suggestions:")
        print("  1. Check your credentials")
        print("  2. Try again later")
        print("  3. Use the manual cookie method")


if __name__ == "__main__":
    main()

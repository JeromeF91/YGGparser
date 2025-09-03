#!/usr/bin/env python3
"""
YGG Torrent Manual Authentication System
Opens browser for manual Cloudflare challenge completion
"""

import requests
import time
import json
import os
import logging
from urllib.parse import urljoin, urlparse
from typing import Dict, Optional, Tuple
import re

try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class YGGManualAuth:
    """Manual authentication system for YGG Torrent with Cloudflare bypass."""
    
    def __init__(self, base_url: str = "https://www.yggtorrent.top"):
        self.base_url = base_url
        self.session = None
        self.driver = None
        self.cookies = {}
        self.logger = self._setup_logging()
        self._setup_session()
    
    def _setup_logging(self):
        """Setup logging for authentication."""
        os.makedirs('logs', exist_ok=True)
        
        logger = logging.getLogger('ygg_manual_auth')
        logger.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler('logs/manual_auth.log')
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _setup_session(self):
        """Setup session with cloudscraper."""
        if CLOUDSCRAPER_AVAILABLE:
            try:
                self.session = cloudscraper.create_scraper(
                    browser={
                        'browser': 'chrome',
                        'platform': 'linux',
                        'mobile': False
                    }
                )
                self.logger.info("✅ Using cloudscraper session")
            except Exception as e:
                self.logger.warning(f"⚠ Cloudscraper failed: {e}")
                self.session = requests.Session()
        else:
            self.session = requests.Session()
        
        # Set headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def authenticate_manual(self, username: str, password: str) -> Tuple[bool, Dict[str, str]]:
        """
        Authenticate using manual Cloudflare challenge completion.
        
        Args:
            username: YGG Torrent username
            password: YGG Torrent password
            
        Returns:
            Tuple of (success, cookies_dict)
        """
        if not SELENIUM_AVAILABLE:
            self.logger.error("❌ Selenium not available. Install with: pip install selenium")
            return False, {}
        
        try:
            self.logger.info("🚀 Starting manual authentication...")
            
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--allow-running-insecure-content')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Create driver (non-headless for manual interaction)
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Navigate to login page
            self.logger.info("📄 Navigating to login page...")
            login_url = f"{self.base_url}/auth/login"
            self.driver.get(login_url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Check for Cloudflare challenge
            page_source = self.driver.page_source.lower()
            title = (self.driver.title or "").lower()
            
            cloudflare_indicators = [
                "just a moment",
                "checking your browser",
                "please wait",
                "ddos protection",
                "cloudflare",
                "cf-browser-verification"
            ]
            
            is_cloudflare = any(indicator in page_source or indicator in title for indicator in cloudflare_indicators)
            
            if is_cloudflare:
                print("\n" + "="*60)
                print("🛡️  CLOUDFLARE CHALLENGE DETECTED")
                print("="*60)
                print("A browser window has opened with the Cloudflare challenge.")
                print("Please complete the 'Verify you are human' challenge manually.")
                print("This may involve:")
                print("  - Clicking a checkbox")
                print("  - Solving a CAPTCHA")
                print("  - Waiting for automatic verification")
                print("\n⏳ The script will wait for you to complete this step...")
                print("="*60)
                
                # Wait for user to complete challenge
                input("\n👤 Press ENTER after you have completed the Cloudflare challenge and can see the login page...")
                
                # Check if challenge is still active
                time.sleep(2)
                new_page_source = self.driver.page_source.lower()
                new_title = (self.driver.title or "").lower()
                still_cloudflare = any(indicator in new_page_source or indicator in new_title for indicator in cloudflare_indicators)
                
                if still_cloudflare:
                    print("\n⚠️  Cloudflare challenge still active!")
                    print("Please make sure you have completed the challenge completely.")
                    print("The page should show the login form, not 'Just a moment...'")
                    input("👤 Press ENTER when you can see the login form with username/password fields...")
                
                # Refresh page to make sure we're on the right page
                self.driver.refresh()
                time.sleep(3)
                
                # Final check
                final_page_source = self.driver.page_source.lower()
                final_title = (self.driver.title or "").lower()
                final_cloudflare = any(indicator in final_page_source or indicator in final_title for indicator in cloudflare_indicators)
                
                if final_cloudflare:
                    print(f"\n❌ Cloudflare challenge still active after refresh!")
                    print(f"📄 Current title: {self.driver.title}")
                    print(f"📄 Current URL: {self.driver.current_url}")
                    print("Please try again and make sure to complete the challenge fully.")
                    return False, {}
            
            # Now try to find and fill the login form
            self.logger.info("🔍 Looking for login form...")
            
            # Wait a bit for form to load
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
                print(f"\n❌ Could not find username field on the page.")
                print(f"📄 Current URL: {self.driver.current_url}")
                print(f"📄 Page title: {self.driver.title}")
                return False, {}
            
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
                print(f"\n❌ Could not find password field on the page.")
                return False, {}
            
            # Fill form
            self.logger.info("📝 Filling login form...")
            username_field.clear()
            username_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)
            
            # Find and click submit button
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
                print(f"\n❌ Could not find submit button on the page.")
                return False, {}
            
            # Click submit
            self.logger.info("🚀 Submitting login form...")
            submit_button.click()
            
            # Wait for login to process
            time.sleep(5)
            
            # Check if login was successful
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            self.logger.info(f"📄 Current URL after login: {current_url}")
            self.logger.info(f"📄 Page title: {self.driver.title}")
            
            # Check for success indicators
            success_indicators = ['logout', 'déconnexion', 'profile', 'profil', 'account', 'compte', 'dashboard']
            failure_indicators = ['login', 'connexion', 'error', 'erreur', 'invalid', 'incorrect']
            
            has_success = any(indicator in page_source for indicator in success_indicators)
            has_failure = any(indicator in page_source for indicator in failure_indicators)
            
            if has_success and not has_failure:
                self.logger.info("✅ Login successful!")
                
                # Get cookies
                selenium_cookies = self.driver.get_cookies()
                self.cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
                
                self.logger.info(f"🍪 Extracted {len(self.cookies)} cookies:")
                for name, value in self.cookies.items():
                    self.logger.info(f"  {name}: {value[:50]}...")
                
                # Transfer cookies to requests session
                for name, value in self.cookies.items():
                    self.session.cookies.set(name, value)
                
                return True, self.cookies
            else:
                self.logger.error("❌ Login failed")
                print(f"\n❌ Login appears to have failed.")
                print(f"📄 Current URL: {current_url}")
                print(f"📄 Page title: {self.driver.title}")
                return False, {}
                
        except Exception as e:
            self.logger.error(f"❌ Authentication error: {e}")
            print(f"\n❌ Authentication error: {e}")
            return False, {}
        finally:
            if self.driver:
                print("\n🔒 Closing browser...")
                self.driver.quit()
    
    def test_authentication(self) -> bool:
        """Test if authentication is working by accessing a protected page."""
        try:
            self.logger.info("🧪 Testing authentication...")
            
            # Try to access a protected page
            test_url = f"{self.base_url}/"
            response = self.session.get(test_url, timeout=30)
            
            if response.status_code == 200:
                page_content = response.text.lower()
                
                # Check for login indicators
                if 'login' in page_content and 'logout' not in page_content:
                    self.logger.error("❌ Authentication test failed - still showing login page")
                    return False
                else:
                    self.logger.info("✅ Authentication test successful!")
                    return True
            else:
                self.logger.error(f"❌ Authentication test failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Authentication test error: {e}")
            return False
    
    def save_cookies(self, filename: str = None) -> str:
        """Save cookies to a file."""
        if filename is None:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f"data/manual_cookies_{timestamp}.json"
        
        os.makedirs('data', exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(self.cookies, f, indent=2)
        
        self.logger.info(f"💾 Cookies saved to: {filename}")
        return filename
    
    def get_cookie_string(self) -> str:
        """Get cookies as a string format."""
        return '; '.join([f"{name}={value}" for name, value in self.cookies.items()])


def main():
    """Main function for manual authentication."""
    print("🚀 YGG Torrent Manual Authentication System")
    print("=" * 50)
    
    auth = YGGManualAuth()
    
    # Get credentials
    username = input("Enter YGG Torrent username: ").strip()
    password = input("Enter YGG Torrent password: ").strip()
    
    if not username or not password:
        print("❌ Username and password are required")
        return
    
    print(f"\n🔐 Attempting to authenticate user: {username}")
    
    # Try manual authentication
    success, cookies = auth.authenticate_manual(username, password)
    
    if success:
        print("✅ Authentication successful!")
        print(f"🍪 Extracted {len(cookies)} cookies")
        
        # Test authentication
        if auth.test_authentication():
            print("✅ Authentication test passed!")
            
            # Save cookies
            cookie_file = auth.save_cookies()
            
            # Show cookie string
            cookie_string = auth.get_cookie_string()
            print(f"\n🍪 Cookie string:")
            print(cookie_string)
            
            print(f"\n💾 Cookies saved to: {cookie_file}")
            print("\n🎉 Manual authentication completed successfully!")
        else:
            print("❌ Authentication test failed")
    else:
        print("❌ Authentication failed")


if __name__ == "__main__":
    main()

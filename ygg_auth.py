#!/usr/bin/env python3
"""
YGG Torrent Real Authentication System
Automatically logs into YGG Torrent and extracts real cookies
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


class YGGRealAuth:
    """Real authentication system for YGG Torrent."""
    
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
        
        logger = logging.getLogger('ygg_real_auth')
        logger.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler('logs/real_auth.log')
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
    
    def authenticate_with_selenium(self, username: str, password: str, headless: bool = True, retry_non_headless: bool = True) -> Tuple[bool, Dict[str, str]]:
        """
        Authenticate using Selenium and extract real cookies.
        
        Args:
            username: YGG Torrent username
            password: YGG Torrent password
            headless: Run browser in headless mode
            
        Returns:
            Tuple of (success, cookies_dict)
        """
        if not SELENIUM_AVAILABLE:
            self.logger.error("❌ Selenium not available. Install with: pip install selenium")
            return False, {}
        
        try:
            self.logger.info("🚀 Starting Selenium authentication...")
            
            # Setup Chrome options with enhanced stealth and Cloudflare bypass
            chrome_options = Options()
            if headless:
                chrome_options.add_argument('--headless')
            
            # Basic options
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--allow-running-insecure-content')
            chrome_options.add_argument('--disable-features=VizDisplayCompositor')
            
            # Enhanced stealth options
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
            
            # User agent and experimental options
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_experimental_option("detach", True)
            
            # Create driver
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Navigate to login page
            self.logger.info("📄 Navigating to login page...")
            login_url = f"{self.base_url}/auth/login"
            self.driver.get(login_url)
            
            # Wait for Cloudflare challenge with improved handling
            self.logger.info("⏳ Waiting for page to load...")
            time.sleep(5)  # Initial wait for page load
            
            # Check for Cloudflare challenge
            cloudflare_indicators = [
                "Just a moment",
                "Checking your browser",
                "Please wait",
                "DDoS protection",
                "cloudflare",
                "cf-browser-verification"
            ]
            
            max_attempts = 5
            attempt = 0
            
            while attempt < max_attempts:
                page_source = self.driver.page_source.lower()
                title = self.driver.title or ""
                title = title.lower()
                
                # Check if we're still on Cloudflare challenge
                is_cloudflare = any(indicator in page_source or indicator in title for indicator in cloudflare_indicators)
                
                if is_cloudflare:
                    self.logger.info(f"⏳ Cloudflare challenge detected (attempt {attempt + 1}/{max_attempts})...")
                    self.logger.info(f"📄 Current title: {self.driver.title}")
                    
                    if not headless:
                        self.logger.info("👤 Manual interaction required - please complete the 'Verify you are human' challenge in the browser window")
                        self.logger.info("⏳ Waiting for you to complete the challenge...")
                        # Wait longer for manual interaction
                        time.sleep(30)
                    else:
                        # Wait longer for challenge to complete automatically
                        time.sleep(15)
                    
                    # Try to detect if challenge completed
                    try:
                        new_page_source = self.driver.page_source.lower()
                        new_title = self.driver.title or ""
                        new_title = new_title.lower()
                        still_cloudflare = any(indicator in new_page_source or indicator in new_title for indicator in cloudflare_indicators)
                    except Exception as e:
                        self.logger.warning(f"⚠️ Error checking challenge status: {e}")
                        still_cloudflare = True  # Assume still in challenge if we can't check
                    
                    if not still_cloudflare:
                        self.logger.info("✅ Cloudflare challenge completed!")
                        break
                    else:
                        attempt += 1
                        if attempt < max_attempts:
                            self.logger.info(f"⏳ Challenge still active, waiting longer... (attempt {attempt + 1})")
                            time.sleep(10)
                        else:
                            self.logger.warning("⚠️ Cloudflare challenge timeout, trying to continue...")
                            # Try to refresh the page
                            self.driver.refresh()
                            time.sleep(10)
                            break
                else:
                    self.logger.info("✅ No Cloudflare challenge detected")
                    break
            
            time.sleep(2)
            
            # Find and fill login form
            self.logger.info("🔍 Looking for login form...")
            
            # Try different selectors for username field
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
                "#login",
                ".username",
                ".login-field"
            ]
            
            username_field = None
            for selector in username_selectors:
                try:
                    username_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    self.logger.info(f"✅ Found username field with selector: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not username_field:
                # Try to find any text input that might be username
                try:
                    text_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
                    if text_inputs:
                        username_field = text_inputs[0]  # Take the first text input
                        self.logger.info("✅ Found username field (first text input)")
                except:
                    pass
            
            if not username_field:
                self.logger.error("❌ Could not find username field")
                self.logger.error(f"📄 Page source preview: {self.driver.page_source[:500]}...")
                return False, {}
            
            # Try different selectors for password field
            password_selectors = [
                "input[name='pass']",
                "input[name='password']",
                "input[name='pwd']",
                "input[type='password']",
                "#pass",
                "#password",
                "#pwd",
                ".password",
                ".pass-field"
            ]
            
            password_field = None
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
                        password_field = password_inputs[0]  # Take the first password input
                        self.logger.info("✅ Found password field (first password input)")
                except:
                    pass
            
            if not password_field:
                self.logger.error("❌ Could not find password field")
                return False, {}
            
            # Fill form
            self.logger.info("📝 Filling login form...")
            username_field.clear()
            username_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)
            
            # Submit form
            submit_selectors = [
                "input[type='submit']",
                "button[type='submit']",
                "input[value='Connexion']",
                "input[value='Login']",
                "input[value='Se connecter']",
                "button:contains('Connexion')",
                "button:contains('Login')",
                "button:contains('Se connecter')",
                ".submit",
                ".login-button",
                "#submit",
                "#login-button"
            ]
            
            submit_button = None
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
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button, input[type="submit"]')
                    button_texts = [btn.get_attribute('value') or btn.text for btn in buttons]
                    self.logger.error(f"📄 Available buttons: {button_texts}")
                except:
                    self.logger.error("📄 Could not get button information")
                return False, {}
            
            # Click submit
            self.logger.info("🚀 Submitting login form...")
            submit_button.click()
            
            # Wait for login
            time.sleep(5)
            
            # Check if successful
            page_source = self.driver.page_source.lower()
            current_url = self.driver.current_url
            
            self.logger.info(f"📄 Current URL: {current_url}")
            self.logger.info(f"📄 Page title: {self.driver.title}")
            
            # Check for success indicators
            success_indicators = ['logout', 'déconnexion', 'profile', 'profil', 'account', 'compte']
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
                self.logger.error(f"Page source contains: {page_source[:500]}...")
                return False, {}
                
        except Exception as e:
            self.logger.error(f"❌ Authentication error: {e}")
            
            # If headless failed and we can retry, try non-headless mode
            if headless and retry_non_headless:
                self.logger.info("🔄 Retrying with non-headless mode...")
                if self.driver:
                    self.driver.quit()
                return self.authenticate_with_selenium(username, password, headless=False, retry_non_headless=False)
            
            return False, {}
        finally:
            if self.driver:
                self.driver.quit()
    
    def authenticate_with_requests(self, username: str, password: str) -> Tuple[bool, Dict[str, str]]:
        """
        Authenticate using requests (fallback method).
        
        Args:
            username: YGG Torrent username
            password: YGG Torrent password
            
        Returns:
            Tuple of (success, cookies_dict)
        """
        try:
            self.logger.info("🚀 Starting requests-based authentication...")
            
            # Get login page
            login_url = f"{self.base_url}/auth/login"
            response = self.session.get(login_url, timeout=30)
            
            if response.status_code != 200:
                self.logger.error(f"❌ Failed to get login page: {response.status_code}")
                return False, {}
            
            self.logger.info("✅ Got login page")
            
            # Look for CSRF token or form data
            page_content = response.text
            
            # Try to find form fields
            import re
            
            # Look for hidden fields
            hidden_fields = re.findall(r'<input[^>]*type="hidden"[^>]*name="([^"]*)"[^>]*value="([^"]*)"', page_content)
            
            form_data = {
                'id': username,
                'pass': password
            }
            
            # Add hidden fields
            for name, value in hidden_fields:
                form_data[name] = value
                self.logger.info(f"📝 Found hidden field: {name}")
            
            # Submit login form
            self.logger.info("🚀 Submitting login form...")
            login_response = self.session.post(login_url, data=form_data, timeout=30)
            
            if login_response.status_code == 200:
                # Check if login was successful
                if 'logout' in login_response.text.lower() or 'déconnexion' in login_response.text.lower():
                    self.logger.info("✅ Login successful!")
                    
                    # Get cookies
                    self.cookies = dict(self.session.cookies)
                    
                    self.logger.info(f"🍪 Extracted {len(self.cookies)} cookies:")
                    for name, value in self.cookies.items():
                        self.logger.info(f"  {name}: {value[:50]}...")
                    
                    return True, self.cookies
                else:
                    self.logger.error("❌ Login failed - still showing login page")
                    return False, {}
            else:
                self.logger.error(f"❌ Login request failed: {login_response.status_code}")
                return False, {}
                
        except Exception as e:
            self.logger.error(f"❌ Requests authentication error: {e}")
            return False, {}
    
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
            filename = f"data/real_cookies_{timestamp}.json"
        
        os.makedirs('data', exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(self.cookies, f, indent=2)
        
        self.logger.info(f"💾 Cookies saved to: {filename}")
        return filename
    
    def load_cookies(self, filename: str) -> bool:
        """Load cookies from a file."""
        try:
            with open(filename, 'r') as f:
                self.cookies = json.load(f)
            
            # Transfer cookies to session
            for name, value in self.cookies.items():
                self.session.cookies.set(name, value)
            
            self.logger.info(f"✅ Loaded {len(self.cookies)} cookies from {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load cookies: {e}")
            return False
    
    def get_cookie_string(self) -> str:
        """Get cookies as a string format."""
        return '; '.join([f"{name}={value}" for name, value in self.cookies.items()])


def main():
    """Main function for testing real authentication."""
    print("🚀 YGG Torrent Real Authentication System")
    print("=" * 50)
    
    auth = YGGRealAuth()
    
    # Get credentials
    username = input("Enter YGG Torrent username: ").strip()
    password = input("Enter YGG Torrent password: ").strip()
    
    if not username or not password:
        print("❌ Username and password are required")
        return
    
    print(f"\n🔐 Attempting to authenticate user: {username}")
    
    # Try Selenium authentication first
    print("\n🌐 Trying Selenium authentication...")
    success, cookies = auth.authenticate_with_selenium(username, password, headless=False)
    
    if not success:
        print("❌ Selenium authentication failed, trying requests method...")
        success, cookies = auth.authenticate_with_requests(username, password)
    
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
            print("\n🎉 Real authentication completed successfully!")
        else:
            print("❌ Authentication test failed")
    else:
        print("❌ Authentication failed")


if __name__ == "__main__":
    main()

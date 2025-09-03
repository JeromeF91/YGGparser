#!/usr/bin/env python3
"""
YGG Torrent Undetected Authentication
Uses undetected-chromedriver to bypass Cloudflare and get cookies automatically
"""

import os
import json
import time
import logging
from typing import Dict, Optional, Tuple


def setup_logging():
    """Setup logging."""
    os.makedirs('logs', exist_ok=True)
    
    logger = logging.getLogger('ygg_undetected_auth')
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger


def try_undetected_chromedriver(username, password):
    """Try using undetected-chromedriver to bypass Cloudflare."""
    logger = setup_logging()
    
    try:
        import undetected_chromedriver as uc
        logger.info("✅ undetected-chromedriver is available")
    except ImportError:
        logger.error("❌ undetected-chromedriver not available. Install with: pip install undetected-chromedriver")
        return False, {}
    
    driver = None
    
    try:
        logger.info("🚀 Starting undetected Chrome driver...")
        
        # Create undetected Chrome driver
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1366,768')
        
        driver = uc.Chrome(options=options)
        
        logger.info("📄 Navigating to YGG Torrent login page...")
        login_url = "https://www.yggtorrent.top/auth/login"
        driver.get(login_url)
        
        # Wait for page to load
        time.sleep(5)
        
        # Check if we're on Cloudflare challenge
        page_source = driver.page_source.lower()
        title = driver.title.lower()
        
        cloudflare_indicators = [
            "just a moment",
            "checking your browser",
            "please wait",
            "ddos protection",
            "cloudflare"
        ]
        
        is_cloudflare = any(indicator in page_source or indicator in title for indicator in cloudflare_indicators)
        
        if is_cloudflare:
            logger.info("⏳ Cloudflare challenge detected, waiting for automatic bypass...")
            # Wait for undetected-chromedriver to handle Cloudflare
            time.sleep(15)
            
            # Check again
            new_page_source = driver.page_source.lower()
            new_title = driver.title.lower()
            still_cloudflare = any(indicator in new_page_source or indicator in new_title for indicator in cloudflare_indicators)
            
            if still_cloudflare:
                logger.warning("⚠️ Cloudflare challenge still active after 15 seconds")
                time.sleep(10)  # Wait a bit more
            else:
                logger.info("✅ Cloudflare challenge bypassed!")
        else:
            logger.info("✅ No Cloudflare challenge detected")
        
        # Now try to find and fill the login form
        logger.info("🔍 Looking for login form...")
        
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
                username_field = driver.find_element("css selector", selector)
                logger.info(f"✅ Found username field: {selector}")
                break
            except:
                continue
        
        if not username_field:
            logger.error("❌ Could not find username field")
            return False, {}
        
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
                password_field = driver.find_element("css selector", selector)
                logger.info(f"✅ Found password field: {selector}")
                break
            except:
                continue
        
        if not password_field:
            logger.error("❌ Could not find password field")
            return False, {}
        
        # Fill form
        logger.info("📝 Filling login form...")
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
            ".submit",
            "#submit"
        ]
        
        for selector in submit_selectors:
            try:
                submit_button = driver.find_element("css selector", selector)
                logger.info(f"✅ Found submit button: {selector}")
                break
            except:
                continue
        
        if not submit_button:
            logger.error("❌ Could not find submit button")
            return False, {}
        
        # Click submit
        logger.info("🚀 Submitting login form...")
        submit_button.click()
        
        # Wait for login
        time.sleep(5)
        
        # Check if login was successful
        current_url = driver.current_url
        page_source = driver.page_source.lower()
        
        logger.info(f"📄 Current URL: {current_url}")
        logger.info(f"📄 Page title: {driver.title}")
        
        # Check for success indicators
        success_indicators = ['logout', 'déconnexion', 'profile', 'profil', 'account', 'compte']
        has_success = any(indicator in page_source for indicator in success_indicators)
        
        if has_success:
            logger.info("✅ Login successful!")
            
            # Extract cookies
            selenium_cookies = driver.get_cookies()
            cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
            
            logger.info(f"🍪 Extracted {len(cookies)} cookies")
            
            return True, cookies
        else:
            logger.error("❌ Login failed")
            return False, {}
            
    except Exception as e:
        logger.error(f"❌ Authentication error: {e}")
        return False, {}
    finally:
        if driver:
            driver.quit()


def try_playwright_auth(username, password):
    """Try using Playwright to bypass Cloudflare."""
    logger = setup_logging()
    
    try:
        from playwright.sync_api import sync_playwright
        logger.info("✅ Playwright is available")
    except ImportError:
        logger.error("❌ Playwright not available. Install with: pip install playwright && playwright install")
        return False, {}
    
    try:
        logger.info("🚀 Starting Playwright browser...")
        
        with sync_playwright() as p:
            # Launch browser with stealth options
            browser = p.chromium.launch(
                headless=False,  # Keep visible for debugging
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            
            # Create context with realistic settings
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1366, 'height': 768}
            )
            
            page = context.new_page()
            
            logger.info("📄 Navigating to YGG Torrent login page...")
            login_url = "https://www.yggtorrent.top/auth/login"
            page.goto(login_url)
            
            # Wait for page to load
            page.wait_for_load_state('networkidle')
            time.sleep(3)
            
            # Check for Cloudflare
            page_source = page.content().lower()
            title = page.title().lower()
            
            cloudflare_indicators = [
                "just a moment",
                "checking your browser",
                "please wait",
                "ddos protection",
                "cloudflare"
            ]
            
            is_cloudflare = any(indicator in page_source or indicator in title for indicator in cloudflare_indicators)
            
            if is_cloudflare:
                logger.info("⏳ Cloudflare challenge detected, waiting...")
                time.sleep(15)
                
                # Check again
                new_page_source = page.content().lower()
                new_title = page.title().lower()
                still_cloudflare = any(indicator in new_page_source or indicator in new_title for indicator in cloudflare_indicators)
                
                if still_cloudflare:
                    logger.warning("⚠️ Cloudflare challenge still active")
                    time.sleep(10)
                else:
                    logger.info("✅ Cloudflare challenge bypassed!")
            else:
                logger.info("✅ No Cloudflare challenge detected")
            
            # Find and fill login form
            logger.info("🔍 Looking for login form...")
            
            # Try to find username field
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
                    username_field = page.query_selector(selector)
                    if username_field:
                        logger.info(f"✅ Found username field: {selector}")
                        break
                except:
                    continue
            
            if not username_field:
                logger.error("❌ Could not find username field")
                return False, {}
            
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
                    password_field = page.query_selector(selector)
                    if password_field:
                        logger.info(f"✅ Found password field: {selector}")
                        break
                except:
                    continue
            
            if not password_field:
                logger.error("❌ Could not find password field")
                return False, {}
            
            # Fill form
            logger.info("📝 Filling login form...")
            username_field.fill(username)
            password_field.fill(password)
            
            # Find and click submit button
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
                    submit_button = page.query_selector(selector)
                    if submit_button:
                        logger.info(f"✅ Found submit button: {selector}")
                        break
                except:
                    continue
            
            if not submit_button:
                logger.error("❌ Could not find submit button")
                return False, {}
            
            # Click submit
            logger.info("🚀 Submitting login form...")
            submit_button.click()
            
            # Wait for login
            page.wait_for_load_state('networkidle')
            time.sleep(3)
            
            # Check if login was successful
            current_url = page.url
            page_source = page.content().lower()
            
            logger.info(f"📄 Current URL: {current_url}")
            logger.info(f"📄 Page title: {page.title()}")
            
            # Check for success indicators
            success_indicators = ['logout', 'déconnexion', 'profile', 'profil', 'account', 'compte']
            has_success = any(indicator in page_source for indicator in success_indicators)
            
            if has_success:
                logger.info("✅ Login successful!")
                
                # Extract cookies
                cookies = context.cookies()
                cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
                
                logger.info(f"🍪 Extracted {len(cookie_dict)} cookies")
                
                return True, cookie_dict
            else:
                logger.error("❌ Login failed")
                return False, {}
            
    except Exception as e:
        logger.error(f"❌ Playwright authentication error: {e}")
        return False, {}


def try_requests_with_cloudscraper(username, password):
    """Try using requests with cloudscraper for authentication."""
    logger = setup_logging()
    
    try:
        import cloudscraper
        logger.info("✅ cloudscraper is available")
    except ImportError:
        logger.error("❌ cloudscraper not available. Install with: pip install cloudscraper")
        return False, {}
    
    try:
        logger.info("🚀 Starting cloudscraper authentication...")
        
        # Create cloudscraper session
        session = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'linux',
                'mobile': False
            }
        )
        
        # Set realistic headers
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Get login page
        logger.info("📄 Getting login page...")
        login_url = "https://www.yggtorrent.top/auth/login"
        response = session.get(login_url, timeout=30)
        
        if response.status_code != 200:
            logger.error(f"❌ Failed to get login page: {response.status_code}")
            return False, {}
        
        logger.info("✅ Got login page")
        
        # Look for form fields and CSRF tokens
        page_content = response.text
        
        # Try to find hidden fields
        import re
        hidden_fields = re.findall(r'<input[^>]*type="hidden"[^>]*name="([^"]*)"[^>]*value="([^"]*)"', page_content)
        
        form_data = {
            'id': username,
            'pass': password
        }
        
        # Add hidden fields
        for name, value in hidden_fields:
            form_data[name] = value
            logger.info(f"📝 Found hidden field: {name}")
        
        # Submit login form
        logger.info("🚀 Submitting login form...")
        login_response = session.post(login_url, data=form_data, timeout=30)
        
        if login_response.status_code == 200:
            # Check if login was successful
            if 'logout' in login_response.text.lower() or 'déconnexion' in login_response.text.lower():
                logger.info("✅ Login successful!")
                
                # Get cookies
                cookies = dict(session.cookies)
                
                logger.info(f"🍪 Extracted {len(cookies)} cookies")
                
                return True, cookies
            else:
                logger.error("❌ Login failed - still showing login page")
                return False, {}
        else:
            logger.error(f"❌ Login request failed: {login_response.status_code}")
            return False, {}
            
    except Exception as e:
        logger.error(f"❌ Cloudscraper authentication error: {e}")
        return False, {}


def main():
    """Main function to test different authentication methods."""
    print("🚀 YGG Torrent Alternative Authentication Methods")
    print("=" * 60)
    print("Testing different approaches to bypass Cloudflare and get cookies automatically.")
    print("=" * 60)
    
    # Get credentials
    username = input("Enter YGG Torrent username: ").strip()
    password = input("Enter YGG Torrent password: ").strip()
    
    if not username or not password:
        print("❌ Username and password are required")
        return
    
    print(f"\n🔐 Testing authentication for user: {username}")
    
    # Test different methods
    methods = [
        ("Undetected ChromeDriver", try_undetected_chromedriver),
        ("Playwright", try_playwright_auth),
        ("Cloudscraper", try_requests_with_cloudscraper)
    ]
    
    for method_name, method_func in methods:
        print(f"\n{'='*60}")
        print(f"🧪 Testing Method: {method_name}")
        print(f"{'='*60}")
        
        try:
            success, cookies = method_func(username, password)
            
            if success:
                print(f"✅ {method_name} authentication successful!")
                print(f"🍪 Extracted {len(cookies)} cookies")
                
                # Save cookies
                os.makedirs('data', exist_ok=True)
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                cookie_file = f"data/{method_name.lower().replace(' ', '_')}_cookies_{timestamp}.json"
                
                with open(cookie_file, 'w') as f:
                    json.dump(cookies, f, indent=2)
                
                print(f"💾 Cookies saved to: {cookie_file}")
                
                # Create cookie string
                cookie_string = '; '.join([f"{name}={value}" for name, value in cookies.items()])
                print(f"🍪 Cookie string: {cookie_string}")
                
                print(f"\n🎉 {method_name} method works! You can use these cookies.")
                return
            else:
                print(f"❌ {method_name} authentication failed")
                
        except Exception as e:
            print(f"❌ {method_name} error: {e}")
    
    print(f"\n❌ All authentication methods failed")
    print("\n💡 Suggestions:")
    print("  1. Check your credentials")
    print("  2. Try again later")
    print("  3. Use the manual cookie method")


if __name__ == "__main__":
    main()

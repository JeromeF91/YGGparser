#!/usr/bin/env python3
"""
YGG API using regular Selenium WebDriver (Linux-compatible)
This version uses standard Selenium instead of undetected-chromedriver
"""

import os
import sys
import json
import time
import logging
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import cloudscraper
import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
LOGIN_URL = "https://www.yggtorrent.top/auth/login"
USERNAME = "JF16v"
PASSWORD = "torrent123"
PASSKEY = "DJdLXYBi2WmyQB0PdNWZ8u9RZEnTqiXT"

# Global variables
current_cookies = None
auth_status = {"authenticated": False, "last_auth": None}

def check_chrome_installation():
    """Check for Chrome/Chromium installation."""
    chrome_paths = [
        '/usr/bin/google-chrome',
        '/usr/bin/google-chrome-stable',
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser',
        '/opt/google/chrome/chrome',
        '/usr/bin/chrome',
        '/snap/bin/chromium'
    ]
    
    found_paths = []
    for path in chrome_paths:
        if os.path.exists(path):
            found_paths.append(path)
    
    if found_paths:
        logger.info(f"Found Chrome/Chromium installations: {found_paths}")
        return found_paths[0]
    else:
        # Try to find Chrome using which command
        try:
            result = subprocess.run(['which', 'google-chrome'], capture_output=True, text=True)
            if result.returncode == 0:
                chrome_path = result.stdout.strip()
                logger.info(f"Found Chrome via which: {chrome_path}")
                return chrome_path
        except:
            pass
        
        try:
            result = subprocess.run(['which', 'chromium'], capture_output=True, text=True)
            if result.returncode == 0:
                chrome_path = result.stdout.strip()
                logger.info(f"Found Chromium via which: {chrome_path}")
                return chrome_path
        except:
            pass
    
    logger.warning("No Chrome/Chromium installation found")
    return None

def is_headless_env():
    """Check if running in headless environment."""
    return (
        not os.environ.get('DISPLAY') or
        os.environ.get('DISPLAY') == ':99' or
        os.path.exists('/.dockerenv') or
        os.environ.get('DOCKER_CONTAINER') or
        os.environ.get('XVFB_RUN') or
        'xvfb' in os.environ.get('_', '') or
        os.environ.get('FORCE_HEADLESS', '').lower() == 'true'
    )

def create_chrome_driver():
    """Create Chrome driver with proper options."""
    chrome_path = check_chrome_installation()
    if not chrome_path:
        raise Exception("No Chrome installation found")
    
    logger.info(f"Using Chrome binary: {chrome_path}")
    
    # Create Chrome options
    options = Options()
    options.binary_location = chrome_path
    
    # Add basic options
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1366,768')
    
    # Add headless options if needed
    if is_headless_env():
        options.add_argument('--headless')
        logger.info("Running in headless environment - using headless mode")
    else:
        logger.info("Running locally - using non-headless mode for better Cloudflare bypass")
    
    # Add additional options for stability
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-plugins')
    options.add_argument('--disable-images')
    options.add_argument('--disable-javascript')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_argument('--virtual-time-budget=5000')
    options.add_argument('--run-all-compositor-stages-before-draw')
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-backgrounding-occluded-windows')
    options.add_argument('--disable-renderer-backgrounding')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-background-networking')
    options.add_argument('--disable-default-apps')
    options.add_argument('--disable-sync')
    options.add_argument('--disable-translate')
    options.add_argument('--hide-scrollbars')
    options.add_argument('--mute-audio')
    options.add_argument('--no-first-run')
    options.add_argument('--disable-logging')
    options.add_argument('--disable-permissions-api')
    options.add_argument('--disable-presentation-api')
    options.add_argument('--disable-print-preview')
    options.add_argument('--disable-speech-api')
    options.add_argument('--disable-file-system')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-geolocation')
    options.add_argument('--disable-media-stream')
    options.add_argument('--disable-client-side-phishing-detection')
    options.add_argument('--disable-component-extensions-with-background-pages')
    options.add_argument('--disable-ipc-flooding-protection')
    options.add_argument('--single-process')
    
    # Try to create driver
    try:
        driver = webdriver.Chrome(options=options)
        logger.info("✅ Chrome driver created successfully")
        return driver
    except Exception as e:
        logger.error(f"Failed to create Chrome driver: {e}")
        raise Exception(f"Could not create Chrome driver: {e}")

def authenticate_with_selenium():
    """Authenticate using regular Selenium WebDriver."""
    logger.info("Starting authentication with regular Selenium...")
    
    driver = None
    try:
        # Create driver
        driver = create_chrome_driver()
        
        # Navigate to login page
        logger.info("Navigating to YGG Torrent login page...")
        driver.get(LOGIN_URL)
        time.sleep(5)
        
        # Check for Cloudflare challenge
        if "cloudflare" in driver.page_source.lower() or "checking your browser" in driver.page_source.lower():
            logger.info("Cloudflare challenge detected, waiting for automatic bypass...")
            time.sleep(15)
            
            if "cloudflare" in driver.page_source.lower():
                logger.warning("Cloudflare challenge still active after 15 seconds")
        
        # Look for login form
        logger.info("Looking for login form...")
        time.sleep(3)
        
        # Save page source for debugging
        os.makedirs('data', exist_ok=True)
        with open('data/debug_selenium_page.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        logger.info("Page source saved to data/debug_selenium_page.html for debugging")
        
        # Find username field
        username_selectors = [
            "input[name='id']",
            "input[name='username']",
            "input[name='user']",
            "input[type='text']",
            "#username",
            "#user",
            "#id"
        ]
        
        username_field = None
        for selector in username_selectors:
            try:
                username_field = driver.find_element(By.CSS_SELECTOR, selector)
                if username_field:
                    logger.info(f"Found username field: {selector}")
                    break
            except:
                continue
        
        if not username_field:
            raise Exception("Could not find username field")
        
        # Find password field
        password_selectors = [
            "input[name='pass']",
            "input[name='password']",
            "input[type='password']",
            "#password",
            "#pass"
        ]
        
        password_field = None
        for selector in password_selectors:
            try:
                password_field = driver.find_element(By.CSS_SELECTOR, selector)
                if password_field:
                    logger.info(f"Found password field: {selector}")
                    break
            except:
                continue
        
        if not password_field:
            raise Exception("Could not find password field")
        
        # Fill login form
        logger.info("Filling login form...")
        username_field.clear()
        username_field.send_keys(USERNAME)
        password_field.clear()
        password_field.send_keys(PASSWORD)
        
        # Find submit button
        submit_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button:contains('Connexion')",
            "button:contains('Login')",
            "button:contains('Se connecter')",
            ".btn-primary",
            "#submit",
            "#login"
        ]
        
        submit_button = None
        for selector in submit_selectors:
            try:
                submit_button = driver.find_element(By.CSS_SELECTOR, selector)
                if submit_button:
                    logger.info(f"Found submit button: {selector}")
                    break
            except:
                continue
        
        if not submit_button:
            raise Exception("Could not find submit button")
        
        # Submit form
        logger.info("Submitting login form...")
        submit_button.click()
        time.sleep(5)
        
        # Check if login was successful
        current_url = driver.current_url
        page_title = driver.title or ""
        
        logger.info(f"Current URL: {current_url}")
        logger.info(f"Page title: {page_title}")
        
        if "login" not in current_url.lower() and "yggtorrent" in page_title.lower():
            logger.info("Login successful!")
            
            # Extract cookies
            cookies = driver.get_cookies()
            logger.info(f"Extracted {len(cookies)} cookies")
            
            # Save cookies
            os.makedirs('data', exist_ok=True)
            cookie_file = f"data/selenium_cookies_{int(time.time())}.json"
            with open(cookie_file, 'w') as f:
                json.dump(cookies, f, indent=2)
            logger.info(f"Cookies saved to: {cookie_file}")
            
            return cookies
        else:
            raise Exception("Login failed - still on login page")
            
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise e
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    chrome_path = check_chrome_installation()
    return jsonify({
        "status": "healthy",
        "chrome_installed": chrome_path is not None,
        "chrome_path": chrome_path,
        "headless_env": is_headless_env(),
        "authenticated": auth_status["authenticated"],
        "driver_type": "selenium"
    })

@app.route('/auth/login', methods=['POST'])
def login():
    """Authenticate and get cookies."""
    global current_cookies, auth_status
    
    try:
        data = request.get_json() or {}
        username = data.get('username', USERNAME)
        password = data.get('password', PASSWORD)
        
        logger.info(f"Authentication request for user: {username}")
        logger.info("Starting authentication for user: {username}")
        
        # Try Selenium authentication
        cookies = authenticate_with_selenium()
        
        current_cookies = cookies
        auth_status = {
            "authenticated": True,
            "last_auth": time.time(),
            "username": username
        }
        
        return jsonify({
            "success": True,
            "message": "Authentication successful",
            "cookies_count": len(cookies),
            "cookies": cookies
        })
        
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 401

@app.route('/auth/status', methods=['GET'])
def auth_status_endpoint():
    """Check authentication status."""
    return jsonify(auth_status)

@app.route('/categories', methods=['GET'])
def get_categories():
    """Get available categories."""
    if not auth_status["authenticated"]:
        return jsonify({"error": "Not authenticated"}), 401
    
    # Return a basic list of categories
    categories = [
        {"id": "2163", "name": "Nintendo Games"},
        {"id": "2164", "name": "PlayStation Games"},
        {"id": "2165", "name": "Xbox Games"},
        {"id": "2166", "name": "PC Games"},
        {"id": "2167", "name": "Movies"},
        {"id": "2168", "name": "TV Shows"},
        {"id": "2169", "name": "Music"},
        {"id": "2170", "name": "Software"},
        {"id": "2171", "name": "Linux"},
        {"id": "2172", "name": "Books"}
    ]
    
    return jsonify({"categories": categories})

@app.route('/rss/<category_id>', methods=['GET'])
def get_rss_feed(category_id):
    """Get RSS feed for a category."""
    if not auth_status["authenticated"]:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        # Parse cookies from request
        cookies_param = request.args.get('cookies', '')
        passkey = request.args.get('passkey', PASSKEY)
        
        if not cookies_param:
            return jsonify({"error": "No cookies provided"}), 400
        
        # Parse cookies string
        cookie_dict = {}
        for cookie in cookies_param.split(';'):
            if '=' in cookie:
                key, value = cookie.strip().split('=', 1)
                cookie_dict[key] = value
        
        # Make RSS request
        rss_url = f"https://www.yggtorrent.top/rss?action=generate&type=subcat&id={category_id}&passkey={passkey}"
        
        session = cloudscraper.create_scraper()
        response = session.get(rss_url, cookies=cookie_dict, timeout=30)
        
        if response.status_code == 200:
            # Parse RSS content
            soup = BeautifulSoup(response.content, 'xml')
            items = []
            
            for item in soup.find_all('item'):
                title = item.find('title')
                link = item.find('link')
                description = item.find('description')
                category = item.find('category')
                
                if title and link:
                    items.append({
                        "title": title.text if title else "",
                        "link": link.text if link else "",
                        "description": description.text if description else "",
                        "category": category.text if category else ""
                    })
            
            return jsonify({
                "success": True,
                "category_id": category_id,
                "items_count": len(items),
                "items": items[:10]  # Return first 10 items
            })
        else:
            return jsonify({
                "success": False,
                "error": f"RSS request failed with status {response.status_code}"
            }), response.status_code
            
    except Exception as e:
        logger.error(f"RSS feed error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='YGG Torrent API with Selenium WebDriver')
    parser.add_argument('--headless', action='store_true', help='Force headless mode')
    parser.add_argument('--port', type=int, default=8080, help='Port to run on')
    args = parser.parse_args()
    
    if args.headless:
        os.environ['FORCE_HEADLESS'] = 'true'
        logger.info("Forcing headless mode via command line argument")
    
    logger.info("Starting YGG Torrent Authentication API (Selenium Version)...")
    logger.info("Available endpoints:")
    logger.info("  GET  /health - Health check")
    logger.info("  POST /auth/login - Authenticate and get cookies")
    logger.info("  GET  /auth/status - Check authentication status")
    logger.info("  GET  /categories - Get available categories")
    logger.info("  GET  /rss/<category_id> - Get RSS feed for category")
    logger.info("")
    logger.info("Usage: python3 ygg_api_selenium_fix.py [--headless] [--port 8080]")
    logger.info("  --headless: Force headless mode (useful for servers without display)")
    logger.info("  --port: Port to run on (default: 8080)")
    
    app.run(host='0.0.0.0', port=args.port, debug=False)

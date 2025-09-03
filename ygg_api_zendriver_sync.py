#!/usr/bin/env python3
"""
YGG Torrent Authentication API using Zendriver and Cloudscraper (Synchronous Version)
A more reliable alternative to undetected-chromedriver
"""

import os
import sys
import json
import logging
import asyncio
import argparse
import threading
from datetime import datetime
from pathlib import Path

import zendriver as zd
import cloudscraper
import requests
from flask import Flask, request, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/ygg_api_zendriver_sync.log')
    ]
)
logger = logging.getLogger(__name__)

# Create necessary directories
Path("data").mkdir(exist_ok=True)
Path("logs").mkdir(exist_ok=True)

app = Flask(__name__)

# Global variables
browser = None
scraper = None
current_cookies = None
last_auth_time = None
auth_lock = threading.Lock()

def check_zendriver_installation():
    """Check if zendriver is properly installed and accessible"""
    try:
        import zendriver
        logger.info("✅ Zendriver is installed and accessible")
        return True
    except ImportError as e:
        logger.error(f"❌ Zendriver not found: {e}")
        logger.error("Install with: pip install zendriver")
        return False

def check_cloudscraper_installation():
    """Check if cloudscraper is properly installed and accessible"""
    try:
        import cloudscraper
        logger.info("✅ Cloudscraper is installed and accessible")
        return True
    except ImportError as e:
        logger.error(f"❌ Cloudscraper not found: {e}")
        logger.error("Install with: pip install cloudscraper")
        return False

def initialize_cloudscraper():
    """Initialize Cloudscraper session"""
    global scraper
    
    try:
        logger.info("🌐 Initializing Cloudscraper session...")
        
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'linux',
                'mobile': False
            },
            delay=1,  # Add small delay between requests
            debug=False
        )
        
        # Set headers to mimic a real browser
        scraper.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        logger.info("✅ Cloudscraper session initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Cloudscraper: {e}")
        return False

def run_async_auth(username, password):
    """Run async authentication in a separate thread"""
    global browser, current_cookies, last_auth_time
    
    try:
        logger.info(f"🔐 Starting authentication for user: {username}")
        
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Initialize browser
        logger.info("🚀 Initializing Zendriver browser...")
        browser = loop.run_until_complete(zd.start(
            headless=True,
            disable_images=True,
            disable_javascript=False,
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ))
        
        # Navigate to login page
        logger.info("🌐 Navigating to YGG Torrent login page...")
        page = loop.run_until_complete(browser.get("https://www.yggtorrent.top/auth/login"))
        
        # Wait for page to load
        loop.run_until_complete(asyncio.sleep(3))
        
        # Check for Cloudflare challenge
        page_content = loop.run_until_complete(page.get_content())
        if "cloudflare" in page_content.lower() or "checking your browser" in page_content.lower():
            logger.info("🛡️ Cloudflare challenge detected, waiting for automatic bypass...")
            loop.run_until_complete(asyncio.sleep(15))  # Wait longer for Cloudflare
        
        # Wait for page to fully load
        logger.info("⏳ Waiting for page to fully load...")
        loop.run_until_complete(asyncio.sleep(5))
        
        # Debug: Save page content to see what we're working with
        page_content = loop.run_until_complete(page.get_content())
        with open("data/debug_zendriver_page.html", "w", encoding="utf-8") as f:
            f.write(page_content)
        logger.info("💾 Page content saved to data/debug_zendriver_page.html for debugging")
        
        # Look for login form with multiple attempts
        logger.info("🔍 Looking for login form...")
        
        # Try different selectors for username field
        username_field = None
        selectors_to_try = [
            "input[name='id']",
            "input[name='username']", 
            "input[name='user']",
            "input[type='text']",
            "input[placeholder*='nom']",
            "input[placeholder*='utilisateur']",
            "input[placeholder*='username']"
        ]
        
        for selector in selectors_to_try:
            try:
                logger.info(f"🔍 Trying selector: {selector}")
                username_field = loop.run_until_complete(page.select(selector))
                if username_field:
                    logger.info(f"✅ Found username field with selector: {selector}")
                    break
            except Exception as e:
                logger.info(f"❌ Selector {selector} failed: {e}")
                continue
        
        if not username_field:
            logger.error("❌ Could not find username field with any selector")
            return False
        
        # Try different selectors for password field
        password_field = None
        password_selectors = [
            "input[name='pass']",
            "input[name='password']",
            "input[type='password']",
            "input[placeholder*='mot de passe']",
            "input[placeholder*='password']"
        ]
        
        for selector in password_selectors:
            try:
                logger.info(f"🔍 Trying password selector: {selector}")
                password_field = loop.run_until_complete(page.select(selector))
                if password_field:
                    logger.info(f"✅ Found password field with selector: {selector}")
                    break
            except Exception as e:
                logger.info(f"❌ Password selector {selector} failed: {e}")
                continue
        
        if not password_field:
            logger.error("❌ Could not find password field with any selector")
            return False
        
        logger.info("✅ Found login form fields")
        
        # Fill login form
        logger.info("📝 Filling login form...")
        loop.run_until_complete(username_field.type(username))
        loop.run_until_complete(password_field.type(password))
        
        # Try different selectors for submit button
        submit_button = None
        submit_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button:contains('Connexion')",
            "button:contains('Login')",
            "input[value*='Connexion']",
            "input[value*='Login']",
            "button",
            "input[type='submit']"
        ]
        
        for selector in submit_selectors:
            try:
                logger.info(f"🔍 Trying submit selector: {selector}")
                submit_button = loop.run_until_complete(page.select(selector))
                if submit_button:
                    logger.info(f"✅ Found submit button with selector: {selector}")
                    break
            except Exception as e:
                logger.info(f"❌ Submit selector {selector} failed: {e}")
                continue
        
        if not submit_button:
            logger.error("❌ Could not find submit button with any selector")
            return False
        
        logger.info("🚀 Submitting login form...")
        loop.run_until_complete(submit_button.click())
        
        # Wait for login to complete
        loop.run_until_complete(asyncio.sleep(5))
        
        # Check if login was successful
        current_url = loop.run_until_complete(page.get_url())
        page_title = loop.run_until_complete(page.get_title())
        
        logger.info(f"📍 Current URL: {current_url}")
        logger.info(f"📄 Page title: {page_title}")
        
        if "login" not in current_url.lower() and "yggtorrent" in page_title.lower():
            logger.info("✅ Login successful!")
            
            # Extract cookies from browser
            cookies = loop.run_until_complete(page.get_cookies())
            logger.info(f"🍪 Extracted {len(cookies)} cookies")
            
            # Convert cookies to format usable by cloudscraper
            cookie_dict = {}
            for cookie in cookies:
                cookie_dict[cookie['name']] = cookie['value']
            
            # Update cloudscraper with cookies
            scraper.cookies.update(cookie_dict)
            current_cookies = cookie_dict
            last_auth_time = datetime.now()
            
            # Save cookies to file
            cookie_file = f"data/api_cookies_zendriver_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(cookie_file, 'w') as f:
                json.dump(cookie_dict, f, indent=2)
            logger.info(f"💾 Cookies saved to: {cookie_file}")
            
            return True
        else:
            logger.error("❌ Login failed - still on login page")
            return False
            
    except Exception as e:
        logger.error(f"❌ Authentication error: {e}")
        return False
    finally:
        # Clean up event loop
        loop.close()

def authenticate_with_zendriver_sync(username, password):
    """Synchronous wrapper for zendriver authentication"""
    with auth_lock:
        return run_async_auth(username, password)

def get_categories_with_cloudscraper():
    """Get categories using cloudscraper with authenticated cookies"""
    global scraper
    
    try:
        logger.info("📂 Fetching categories with Cloudscraper...")
        
        if not scraper:
            logger.error("❌ Cloudscraper not initialized")
            return None
        
        # Try to get categories from RSS page
        response = scraper.get("https://www.yggtorrent.top/rss")
        
        if response.status_code == 200:
            logger.info("✅ Successfully fetched categories")
            return response.text
        else:
            logger.error(f"❌ Failed to fetch categories: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error fetching categories: {e}")
        return None

def get_rss_feed_with_cloudscraper(category_id, passkey):
    """Get RSS feed using cloudscraper with authenticated cookies"""
    global scraper
    
    try:
        logger.info(f"📡 Fetching RSS feed for category {category_id}...")
        
        if not scraper:
            logger.error("❌ Cloudscraper not initialized")
            return None
        
        # Build RSS URL
        rss_url = f"https://www.yggtorrent.top/rss?action=generate&type=subcat&id={category_id}&passkey={passkey}"
        
        # Make request with cloudscraper
        response = scraper.get(rss_url)
        
        if response.status_code == 200:
            logger.info("✅ Successfully fetched RSS feed")
            return response.text
        else:
            logger.error(f"❌ Failed to fetch RSS feed: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error fetching RSS feed: {e}")
        return None

# Flask API Routes

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    zendriver_ok = check_zendriver_installation()
    cloudscraper_ok = check_cloudscraper_installation()
    browser_ok = browser is not None
    scraper_ok = scraper is not None
    
    status = {
        'status': 'healthy' if all([zendriver_ok, cloudscraper_ok, browser_ok, scraper_ok]) else 'unhealthy',
        'zendriver': 'installed' if zendriver_ok else 'not_installed',
        'cloudscraper': 'installed' if cloudscraper_ok else 'not_installed',
        'browser': 'initialized' if browser_ok else 'not_initialized',
        'scraper': 'initialized' if scraper_ok else 'not_initialized',
        'last_auth': last_auth_time.isoformat() if last_auth_time else None,
        'cookies_available': current_cookies is not None
    }
    
    return jsonify(status)

@app.route('/auth/login', methods=['POST'])
def login():
    """Authenticate and get cookies"""
    try:
        data = request.get_json()
        username = data.get('username', 'JF16v')
        password = data.get('password', 'torrent123')
        
        logger.info(f"🔐 Authentication request for user: {username}")
        
        # Run authentication in separate thread
        success = authenticate_with_zendriver_sync(username, password)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Authentication successful',
                'cookies_count': len(current_cookies) if current_cookies else 0,
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Authentication failed'
            }), 401
            
    except Exception as e:
        logger.error(f"❌ Login endpoint error: {e}")
        return jsonify({
            'success': False,
            'message': f'Login error: {str(e)}'
        }), 500

@app.route('/auth/status', methods=['GET'])
def auth_status():
    """Check authentication status"""
    return jsonify({
        'authenticated': current_cookies is not None,
        'last_auth': last_auth_time.isoformat() if last_auth_time else None,
        'cookies_count': len(current_cookies) if current_cookies else 0
    })

@app.route('/categories', methods=['GET'])
def get_categories():
    """Get available categories"""
    try:
        categories_html = get_categories_with_cloudscraper()
        
        if categories_html:
            return jsonify({
                'success': True,
                'categories_html': categories_html,
                'message': 'Categories fetched successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to fetch categories'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Categories endpoint error: {e}")
        return jsonify({
            'success': False,
            'message': f'Categories error: {str(e)}'
        }), 500

@app.route('/rss/<int:category_id>', methods=['GET'])
def get_rss(category_id):
    """Get RSS feed for category"""
    try:
        passkey = request.args.get('passkey', 'DJdLXYBi2WmyQB0PdNWZ8u9RZEnTqiXT')
        
        rss_content = get_rss_feed_with_cloudscraper(category_id, passkey)
        
        if rss_content:
            return jsonify({
                'success': True,
                'rss_content': rss_content,
                'category_id': category_id,
                'passkey': passkey,
                'message': 'RSS feed fetched successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to fetch RSS feed'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ RSS endpoint error: {e}")
        return jsonify({
            'success': False,
            'message': f'RSS error: {str(e)}'
        }), 500

def main():
    """Main function to initialize and run the API"""
    global scraper
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='YGG Torrent API with Zendriver and Cloudscraper (Sync)')
    parser.add_argument('--headless', action='store_true', help='Force headless mode')
    args = parser.parse_args()
    
    logger.info("🚀 Starting YGG Torrent Authentication API with Zendriver and Cloudscraper (Sync)...")
    logger.info("📋 Available endpoints:")
    logger.info("  GET  /health - Health check")
    logger.info("  POST /auth/login - Authenticate and get cookies")
    logger.info("  GET  /auth/status - Check authentication status")
    logger.info("  GET  /categories - Get available categories")
    logger.info("  GET  /rss/<category_id> - Get RSS feed for category")
    logger.info("")
    logger.info("💡 Usage: python3 ygg_api_zendriver_sync.py [--headless]")
    logger.info("  --headless: Force headless mode (useful for servers without display)")
    
    # Check dependencies
    if not check_zendriver_installation():
        logger.error("❌ Zendriver not available. Install with: pip install zendriver")
        sys.exit(1)
    
    if not check_cloudscraper_installation():
        logger.error("❌ Cloudscraper not available. Install with: pip install cloudscraper")
        sys.exit(1)
    
    # Initialize cloudscraper
    logger.info("🔧 Initializing Cloudscraper...")
    scraper_ok = initialize_cloudscraper()
    
    if not scraper_ok:
        logger.error("❌ Failed to initialize cloudscraper")
        sys.exit(1)
    
    # Start Flask app
    logger.info("🌐 Starting Flask API server...")
    app.run(host='0.0.0.0', port=8080, debug=False)

if __name__ == '__main__':
    main()

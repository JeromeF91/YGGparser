#!/usr/bin/env python3
"""
YGG Torrent Authentication API
REST API for remote authentication and cookie generation
"""

import os
import json
import time
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import undetected_chromedriver as uc


# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
BASE_URL = "https://www.yggtorrent.top"
LOGIN_URL = f"{BASE_URL}/auth/login"


def check_chrome_installation():
    """Check if Chrome/Chromium is properly installed and accessible."""
    possible_paths = [
        # Linux paths
        '/usr/bin/google-chrome',
        '/usr/bin/google-chrome-stable',
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser',
        '/usr/bin/chromium-browser-stable',
        '/snap/bin/chromium',
        '/opt/google/chrome/chrome',
        '/usr/local/bin/chromium',
        '/usr/local/bin/google-chrome',
        # macOS paths
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '/Applications/Chromium.app/Contents/MacOS/Chromium',
        # Windows paths
        'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
        'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
        'C:\\Program Files\\Chromium\\Application\\chrome.exe'
    ]
    
    found_paths = []
    for path in possible_paths:
        if os.path.exists(path):
            found_paths.append(path)
    
    if found_paths:
        logger.info(f"Found Chrome/Chromium installations: {found_paths}")
        return found_paths[0]  # Return first found path
    else:
        logger.warning("No Chrome/Chromium installation found in common locations")
        
        # Try to find Chrome using system commands
        import subprocess
        try:
            # Try 'which' command
            result = subprocess.run(['which', 'google-chrome'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                chrome_path = result.stdout.strip()
                logger.info(f"Found Chrome via 'which' command: {chrome_path}")
                return chrome_path
        except:
            pass
        
        try:
            # Try 'which chromium'
            result = subprocess.run(['which', 'chromium'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                chrome_path = result.stdout.strip()
                logger.info(f"Found Chromium via 'which' command: {chrome_path}")
                return chrome_path
        except:
            pass
        
        try:
            # Try 'which chromium-browser'
            result = subprocess.run(['which', 'chromium-browser'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                chrome_path = result.stdout.strip()
                logger.info(f"Found Chromium via 'which chromium-browser' command: {chrome_path}")
                return chrome_path
        except:
            pass
        
        logger.warning("Could not find Chrome/Chromium using system commands either")
        return None


def authenticate_with_undetected_chromedriver(username, password):
    """Authenticate using undetected-chromedriver and return cookies."""
    logger.info(f"Starting authentication for user: {username}")
    
    # Check Chrome installation first
    chrome_path = check_chrome_installation()
    
    driver = None
    
    try:
        # Create undetected Chrome driver (simplified like working script)
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1366,768')
        
        # Check if running in Docker (headless mode)
        import os
        if os.path.exists('/.dockerenv') or os.environ.get('DOCKER_CONTAINER'):
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--remote-debugging-port=9222')
            logger.info("Running in Docker - using headless mode")
        else:
            logger.info("Running locally - using non-headless mode for better Cloudflare bypass")
        
        # Use the Chrome path we already checked
        
        # Create driver with proper error handling
        try:
            if chrome_path:
                logger.info(f"Using Chrome binary: {chrome_path}")
                driver = uc.Chrome(options=options, browser_executable_path=chrome_path)
            else:
                logger.info("No Chrome path found, using auto-detection")
                driver = uc.Chrome(options=options)
        except Exception as e:
            logger.error(f"Failed to create Chrome driver: {e}")
            # Try without specifying binary path as fallback
            try:
                logger.info("Trying fallback: Chrome driver without binary path")
                driver = uc.Chrome(options=options)
            except Exception as e2:
                logger.error(f"Fallback also failed: {e2}")
                raise Exception(f"Could not create Chrome driver. Please install Chrome/Chromium. Original error: {e}, Fallback error: {e2}")
        
        logger.info("Navigating to YGG Torrent login page...")
        driver.get(LOGIN_URL)
        
        # Wait for page to load
        time.sleep(5)
        
        # Check if we're on Cloudflare challenge (simplified like working script)
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
        
        # Find and fill the login form
        logger.info("Looking for login form...")
        time.sleep(3)
        
        # Debug: Save page source for inspection
        try:
            with open('data/debug_api_page.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            logger.info("Page source saved to data/debug_api_page.html for debugging")
        except Exception as e:
            logger.warning(f"Could not save debug page: {e}")
        
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
                logger.info(f"Found username field: {selector}")
                break
            except:
                continue
        
        if not username_field:
            raise Exception("Could not find username field")
        
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
                logger.info(f"Found password field: {selector}")
                break
            except:
                continue
        
        if not password_field:
            raise Exception("Could not find password field")
        
        # Fill form
        logger.info("Filling login form...")
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
                logger.info(f"Found submit button: {selector}")
                break
            except:
                continue
        
        if not submit_button:
            raise Exception("Could not find submit button")
        
        # Click submit
        logger.info("Submitting login form...")
        submit_button.click()
        
        # Wait for login
        time.sleep(5)
        
        # Check if login was successful
        current_url = driver.current_url
        page_source = driver.page_source.lower()
        
        logger.info(f"Current URL: {current_url}")
        logger.info(f"Page title: {driver.title}")
        
        # Check for success indicators
        success_indicators = ['logout', 'déconnexion', 'profile', 'profil', 'account', 'compte']
        has_success = any(indicator in page_source for indicator in success_indicators)
        
        if has_success:
            logger.info("Login successful!")
            
            # Extract cookies
            selenium_cookies = driver.get_cookies()
            cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
            
            logger.info(f"Extracted {len(cookies)} cookies")
            
            return {
                'success': True,
                'cookies': cookies,
                'cookie_string': '; '.join([f"{name}={value}" for name, value in cookies.items()]),
                'message': 'Authentication successful'
            }
        else:
            logger.error("Login failed")
            return {
                'success': False,
                'cookies': {},
                'cookie_string': '',
                'message': 'Login failed - still showing login page'
            }
            
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return {
            'success': False,
            'cookies': {},
            'cookie_string': '',
            'message': f'Authentication error: {str(e)}'
        }
    finally:
        if driver:
            driver.quit()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint with Chrome installation status."""
    chrome_path = check_chrome_installation()
    
    health_data = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'YGG Torrent Authentication API',
        'chrome': {
            'installed': chrome_path is not None,
            'path': chrome_path
        }
    }
    
    if chrome_path:
        health_data['status'] = 'healthy'
    else:
        health_data['status'] = 'warning'
        health_data['message'] = 'Chrome/Chromium not found in common locations'
    
    return jsonify(health_data)


@app.route('/auth/login', methods=['POST'])
def authenticate():
    """Authenticate and generate cookies."""
    try:
        # Get credentials from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400
        
        logger.info(f"Authentication request for user: {username}")
        
        # Authenticate
        result = authenticate_with_undetected_chromedriver(username, password)
        
        if result['success']:
            # Save cookies to file
            os.makedirs('data', exist_ok=True)
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            cookie_file = f"data/api_cookies_{timestamp}.json"
            
            cookie_data = {
                'username': username,
                'cookies': result['cookies'],
                'cookie_string': result['cookie_string'],
                'generated_at': datetime.now().isoformat(),
                'timestamp': timestamp
            }
            
            with open(cookie_file, 'w') as f:
                json.dump(cookie_data, f, indent=2)
            
            logger.info(f"Cookies saved to: {cookie_file}")
            
            return jsonify({
                'success': True,
                'message': 'Authentication successful',
                'cookies': result['cookies'],
                'cookie_string': result['cookie_string'],
                'generated_at': datetime.now().isoformat(),
                'cookie_file': cookie_file
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 401
            
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({
            'success': False,
            'message': f'Internal server error: {str(e)}'
        }), 500


@app.route('/auth/status', methods=['GET'])
def auth_status():
    """Check authentication status with provided cookies."""
    try:
        # Get cookie string from query parameter
        cookie_string = request.args.get('cookies')
        
        if not cookie_string:
            return jsonify({
                'success': False,
                'message': 'Cookie string is required'
            }), 400
        
        # Parse cookies
        cookies = {}
        for cookie in cookie_string.split(';'):
            if '=' in cookie:
                name, value = cookie.strip().split('=', 1)
                cookies[name] = value
        
        # Test cookies by accessing main page
        import requests
        import cloudscraper
        
        session = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'linux',
                'mobile': False
            }
        )
        
        # Set cookies
        for name, value in cookies.items():
            session.cookies.set(name, value)
        
        # Test access
        response = session.get(BASE_URL, timeout=30)
        
        if response.status_code == 200:
            # Check if we're logged in
            page_content = response.text.lower()
            success_indicators = ['logout', 'déconnexion', 'profile', 'profil', 'account', 'compte']
            is_logged_in = any(indicator in page_content for indicator in success_indicators)
            
            return jsonify({
                'success': True,
                'authenticated': is_logged_in,
                'status_code': response.status_code,
                'message': 'Authenticated' if is_logged_in else 'Not authenticated'
            })
        else:
            return jsonify({
                'success': False,
                'authenticated': False,
                'status_code': response.status_code,
                'message': f'HTTP {response.status_code}'
            })
            
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return jsonify({
            'success': False,
            'message': f'Error checking status: {str(e)}'
        }), 500


@app.route('/categories', methods=['GET'])
def get_categories():
    """Get available categories."""
    try:
        # Load categories from file
        categories_file = 'data/extracted_categories_simple.json'
        
        if os.path.exists(categories_file):
            with open(categories_file, 'r') as f:
                categories = json.load(f)
            
            return jsonify({
                'success': True,
                'categories': categories,
                'count': len(categories)
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Categories file not found. Please run category discovery first.'
            }), 404
            
    except Exception as e:
        logger.error(f"Categories error: {e}")
        return jsonify({
            'success': False,
            'message': f'Error loading categories: {str(e)}'
        }), 500


@app.route('/rss/<int:category_id>', methods=['GET'])
def get_rss_feed(category_id):
    """Get RSS feed for a specific category."""
    try:
        # Get cookie string from query parameter
        cookie_string = request.args.get('cookies')
        passkey = request.args.get('passkey')
        
        if not cookie_string:
            return jsonify({
                'success': False,
                'message': 'Cookie string is required'
            }), 400
        
        if not passkey:
            return jsonify({
                'success': False,
                'message': 'Passkey is required'
            }), 400
        
        # Parse cookies
        cookies = {}
        for cookie in cookie_string.split(';'):
            if '=' in cookie:
                name, value = cookie.strip().split('=', 1)
                cookies[name] = value
        
        logger.info(f"Parsed {len(cookies)} cookies for RSS request")
        
        # Get RSS feed
        import requests
        import cloudscraper
        import xml.etree.ElementTree as ET
        
        session = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'linux',
                'mobile': False
            }
        )
        
        # Set cookies
        for name, value in cookies.items():
            session.cookies.set(name, value)
        
        rss_url = f"{BASE_URL}/rss?action=generate&type=subcat&id={category_id}&passkey={passkey}"
        
        response = session.get(rss_url, timeout=30)
        
        if response.status_code == 200:
            # Parse RSS
            root = ET.fromstring(response.text)
            items = root.findall('.//item')
            
            torrents = []
            for item in items:
                title = item.find('title')
                link = item.find('link')
                category = item.find('category')
                
                if title is not None and link is not None:
                    torrent_id = link.text.split('/')[-1].split('-')[0]
                    torrents.append({
                        'id': torrent_id,
                        'title': title.text,
                        'link': link.text,
                        'category': category.text if category is not None else 'Unknown'
                    })
            
            return jsonify({
                'success': True,
                'category_id': category_id,
                'torrents': torrents,
                'count': len(torrents)
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Failed to get RSS feed: HTTP {response.status_code}'
            }), response.status_code
            
    except Exception as e:
        logger.error(f"RSS feed error: {e}")
        return jsonify({
            'success': False,
            'message': f'Error getting RSS feed: {str(e)}'
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'message': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500


if __name__ == '__main__':
    logger.info("Starting YGG Torrent Authentication API...")
    logger.info("Available endpoints:")
    logger.info("  GET  /health - Health check")
    logger.info("  POST /auth/login - Authenticate and get cookies")
    logger.info("  GET  /auth/status - Check authentication status")
    logger.info("  GET  /categories - Get available categories")
    logger.info("  GET  /rss/<category_id> - Get RSS feed for category")
    
    app.run(host='0.0.0.0', port=8080, debug=False)

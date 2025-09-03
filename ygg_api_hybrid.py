#!/usr/bin/env python3
"""
YGG Torrent Hybrid API - Manual auth + Cookie-based requests
Uses manual authentication to get cookies, then provides API endpoints
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path

import cloudscraper
import requests
from flask import Flask, request, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/ygg_api_hybrid.log')
    ]
)
logger = logging.getLogger(__name__)

# Create necessary directories
Path("data").mkdir(exist_ok=True)
Path("logs").mkdir(exist_ok=True)

app = Flask(__name__)

# Global variables
scraper = None
current_cookies = None
last_auth_time = None

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

def load_cookies_from_file():
    """Load cookies from the most recent manual authentication file"""
    global current_cookies, last_auth_time
    
    try:
        # Look for manual cookie files
        data_dir = Path("data")
        cookie_files = list(data_dir.glob("manual_cookies_*.json"))
        
        if not cookie_files:
            logger.warning("⚠️ No manual cookie files found")
            return False
        
        # Get the most recent file
        latest_file = max(cookie_files, key=lambda f: f.stat().st_mtime)
        logger.info(f"📂 Loading cookies from: {latest_file}")
        
        with open(latest_file, 'r') as f:
            cookies = json.load(f)
        
        if cookies:
            current_cookies = cookies
            last_auth_time = datetime.fromtimestamp(latest_file.stat().st_mtime)
            scraper.cookies.update(cookies)
            logger.info(f"✅ Loaded {len(cookies)} cookies from {latest_file}")
            return True
        else:
            logger.error("❌ No cookies found in file")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to load cookies: {e}")
        return False

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
    cloudscraper_ok = check_cloudscraper_installation()
    scraper_ok = scraper is not None
    cookies_ok = current_cookies is not None
    
    status = {
        'status': 'healthy' if all([cloudscraper_ok, scraper_ok, cookies_ok]) else 'unhealthy',
        'cloudscraper': 'installed' if cloudscraper_ok else 'not_installed',
        'scraper': 'initialized' if scraper_ok else 'not_initialized',
        'cookies': 'loaded' if cookies_ok else 'not_loaded',
        'last_auth': last_auth_time.isoformat() if last_auth_time else None,
        'cookies_count': len(current_cookies) if current_cookies else 0
    }
    
    return jsonify(status)

@app.route('/auth/status', methods=['GET'])
def auth_status():
    """Check authentication status"""
    return jsonify({
        'authenticated': current_cookies is not None,
        'last_auth': last_auth_time.isoformat() if last_auth_time else None,
        'cookies_count': len(current_cookies) if current_cookies else 0
    })

@app.route('/auth/load-cookies', methods=['POST'])
def load_cookies():
    """Load cookies from manual authentication"""
    try:
        success = load_cookies_from_file()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Cookies loaded successfully',
                'cookies_count': len(current_cookies) if current_cookies else 0,
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to load cookies. Run manual authentication first.'
            }), 400
            
    except Exception as e:
        logger.error(f"❌ Load cookies endpoint error: {e}")
        return jsonify({
            'success': False,
            'message': f'Load cookies error: {str(e)}'
        }), 500

@app.route('/categories', methods=['GET'])
def get_categories():
    """Get available categories"""
    try:
        if not current_cookies:
            return jsonify({
                'success': False,
                'message': 'No cookies loaded. Run manual authentication first.'
            }), 401
        
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
        if not current_cookies:
            return jsonify({
                'success': False,
                'message': 'No cookies loaded. Run manual authentication first.'
            }), 401
        
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
    parser = argparse.ArgumentParser(description='YGG Torrent Hybrid API - Manual auth + Cookie-based requests')
    args = parser.parse_args()
    
    logger.info("🚀 Starting YGG Torrent Hybrid API...")
    logger.info("📋 Available endpoints:")
    logger.info("  GET  /health - Health check")
    logger.info("  GET  /auth/status - Check authentication status")
    logger.info("  POST /auth/load-cookies - Load cookies from manual authentication")
    logger.info("  GET  /categories - Get available categories")
    logger.info("  GET  /rss/<category_id> - Get RSS feed for category")
    logger.info("")
    logger.info("💡 Usage:")
    logger.info("  1. Run: python3 ygg_manual_auth.py (to get cookies)")
    logger.info("  2. Run: python3 ygg_api_hybrid.py (to start API)")
    logger.info("  3. POST /auth/load-cookies (to load cookies into API)")
    
    # Check dependencies
    if not check_cloudscraper_installation():
        logger.error("❌ Cloudscraper not available. Install with: pip install cloudscraper")
        sys.exit(1)
    
    # Initialize cloudscraper
    logger.info("🔧 Initializing Cloudscraper...")
    scraper_ok = initialize_cloudscraper()
    
    if not scraper_ok:
        logger.error("❌ Failed to initialize cloudscraper")
        sys.exit(1)
    
    # Try to load existing cookies
    logger.info("🔍 Looking for existing cookies...")
    load_cookies_from_file()
    
    # Start Flask app
    logger.info("🌐 Starting Flask API server...")
    app.run(host='0.0.0.0', port=8080, debug=False)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Test script for Zendriver + Cloudscraper combination
"""

import asyncio
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_zendriver_installation():
    """Test if zendriver is properly installed"""
    try:
        import zendriver as zd
        logger.info("✅ Zendriver is installed and accessible")
        return True
    except ImportError as e:
        logger.error(f"❌ Zendriver not found: {e}")
        logger.error("Install with: pip install zendriver")
        return False

def test_cloudscraper_installation():
    """Test if cloudscraper is properly installed"""
    try:
        import cloudscraper
        logger.info("✅ Cloudscraper is installed and accessible")
        return True
    except ImportError as e:
        logger.error(f"❌ Cloudscraper not found: {e}")
        logger.error("Install with: pip install cloudscraper")
        return False

async def test_zendriver_basic():
    """Test basic zendriver functionality"""
    try:
        import zendriver as zd
        
        logger.info("🧪 Testing Zendriver basic functionality...")
        
        # Test headless mode
        logger.info("🔧 Testing headless mode...")
        browser = await zd.start(headless=True, disable_images=True)
        
        page = await browser.get("https://httpbin.org/user-agent")
        content = await page.get_content()
        
        if "user-agent" in content.lower():
            logger.info("✅ Zendriver headless test successful")
        else:
            logger.error("❌ Zendriver headless test failed")
            return False
        
        # Zendriver doesn't have a close method - it's managed automatically
        return True
        
    except Exception as e:
        logger.error(f"❌ Zendriver test failed: {e}")
        return False

def test_cloudscraper_basic():
    """Test basic cloudscraper functionality"""
    try:
        import cloudscraper
        
        logger.info("🧪 Testing Cloudscraper basic functionality...")
        
        scraper = cloudscraper.create_scraper()
        response = scraper.get("https://httpbin.org/user-agent")
        
        if response.status_code == 200:
            logger.info("✅ Cloudscraper test successful")
            return True
        else:
            logger.error(f"❌ Cloudscraper test failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Cloudscraper test failed: {e}")
        return False

async def test_zendriver_cloudscraper_integration():
    """Test integration between zendriver and cloudscraper"""
    try:
        import zendriver as zd
        import cloudscraper
        
        logger.info("🧪 Testing Zendriver + Cloudscraper integration...")
        
        # Initialize browser
        browser = await zd.start(headless=True, disable_images=True)
        page = await browser.get("https://httpbin.org/cookies")
        
        # Get cookies from zendriver
        cookies = await page.get_cookies()
        logger.info(f"🍪 Extracted {len(cookies)} cookies from Zendriver")
        
        # Convert to cloudscraper format
        cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
        
        # Initialize cloudscraper with cookies
        scraper = cloudscraper.create_scraper()
        scraper.cookies.update(cookie_dict)
        
        # Test request with cloudscraper
        response = scraper.get("https://httpbin.org/cookies")
        
        if response.status_code == 200:
            logger.info("✅ Zendriver + Cloudscraper integration test successful")
            return True
        else:
            logger.error(f"❌ Integration test failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")
        return False

async def test_ygg_torrent_access():
    """Test accessing YGG Torrent with zendriver + cloudscraper"""
    try:
        import zendriver as zd
        import cloudscraper
        
        logger.info("🧪 Testing YGG Torrent access...")
        
        # Initialize browser
        browser = await zd.start(headless=True, disable_images=True)
        page = await browser.get("https://www.yggtorrent.top/")
        
        # Wait for page to load
        await asyncio.sleep(3)
        
        # Check for Cloudflare
        content = await page.get_content()
        if "cloudflare" in content.lower() or "checking your browser" in content.lower():
            logger.info("🛡️ Cloudflare challenge detected, waiting...")
            await asyncio.sleep(10)
        
        # Get cookies
        cookies = await page.get_cookies()
        logger.info(f"🍪 Extracted {len(cookies)} cookies")
        
        # Test with cloudscraper
        cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
        scraper = cloudscraper.create_scraper()
        scraper.cookies.update(cookie_dict)
        
        # Try to access RSS page
        response = scraper.get("https://www.yggtorrent.top/rss")
        
        if response.status_code == 200:
            logger.info("✅ YGG Torrent access test successful")
            return True
        else:
            logger.error(f"❌ YGG Torrent access failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ YGG Torrent test failed: {e}")
        return False

async def main():
    """Run all tests"""
    logger.info("🚀 Starting Zendriver + Cloudscraper compatibility tests...")
    
    # Test installations
    zendriver_ok = await test_zendriver_installation()
    cloudscraper_ok = test_cloudscraper_installation()
    
    if not zendriver_ok or not cloudscraper_ok:
        logger.error("❌ Missing dependencies. Please install required packages.")
        sys.exit(1)
    
    # Test basic functionality
    zendriver_basic_ok = await test_zendriver_basic()
    cloudscraper_basic_ok = test_cloudscraper_basic()
    
    if not zendriver_basic_ok or not cloudscraper_basic_ok:
        logger.error("❌ Basic functionality tests failed.")
        sys.exit(1)
    
    # Test integration
    integration_ok = await test_zendriver_cloudscraper_integration()
    
    if not integration_ok:
        logger.error("❌ Integration test failed.")
        sys.exit(1)
    
    # Test YGG Torrent access
    ygg_ok = await test_ygg_torrent_access()
    
    if ygg_ok:
        logger.info("🎉 All tests passed! Zendriver + Cloudscraper is ready to use.")
    else:
        logger.warning("⚠️ YGG Torrent access test failed, but basic functionality works.")
        logger.info("💡 You can still try the API - it might work with authentication.")

if __name__ == '__main__':
    asyncio.run(main())

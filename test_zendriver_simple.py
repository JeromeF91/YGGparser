#!/usr/bin/env python3
"""
Simple test script for Zendriver functionality
"""

import asyncio
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_zendriver_simple():
    """Simple zendriver test without browser.close()"""
    try:
        import zendriver as zd
        
        logger.info("🧪 Testing Zendriver simple functionality...")
        
        # Test headless mode
        logger.info("🔧 Testing headless mode...")
        browser = await zd.start(headless=True, disable_images=True)
        
        page = await browser.get("https://httpbin.org/user-agent")
        content = await page.get_content()
        
        if "user-agent" in content.lower():
            logger.info("✅ Zendriver test successful")
            return True
        else:
            logger.error("❌ Zendriver test failed")
            return False
        
    except Exception as e:
        logger.error(f"❌ Zendriver test failed: {e}")
        return False

def test_cloudscraper_simple():
    """Simple cloudscraper test"""
    try:
        import cloudscraper
        
        logger.info("🧪 Testing Cloudscraper simple functionality...")
        
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

async def main():
    """Run simple tests"""
    logger.info("🚀 Starting simple Zendriver + Cloudscraper tests...")
    
    # Test cloudscraper first (synchronous)
    cloudscraper_ok = test_cloudscraper_simple()
    
    if not cloudscraper_ok:
        logger.error("❌ Cloudscraper test failed.")
        sys.exit(1)
    
    # Test zendriver (asynchronous)
    zendriver_ok = await test_zendriver_simple()
    
    if zendriver_ok:
        logger.info("🎉 All simple tests passed! Ready to try the API.")
    else:
        logger.error("❌ Zendriver test failed.")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())

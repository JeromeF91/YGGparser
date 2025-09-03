#!/usr/bin/env python3
"""
Test script to understand zendriver API
"""

import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_zendriver_api():
    """Test zendriver API methods"""
    try:
        import zendriver as zd
        
        logger.info("🧪 Testing Zendriver API methods...")
        
        # Start browser
        browser = await zd.start(headless=True, disable_images=True)
        logger.info("✅ Browser started")
        
        # Get page
        page = await browser.get("https://httpbin.org/forms/post")
        logger.info("✅ Page loaded")
        
        # Check page object type and methods
        logger.info(f"📄 Page object type: {type(page)}")
        logger.info(f"📋 Page object methods: {[method for method in dir(page) if not method.startswith('_')]}")
        
        # Try different methods to find elements
        try:
            # Method 1: query_selector
            element = await page.query_selector("input[name='custname']")
            if element:
                logger.info("✅ query_selector works")
            else:
                logger.info("❌ query_selector returned None")
        except Exception as e:
            logger.error(f"❌ query_selector failed: {e}")
        
        try:
            # Method 2: query_selector_all
            elements = await page.query_selector_all("input")
            logger.info(f"✅ query_selector_all found {len(elements)} elements")
        except Exception as e:
            logger.error(f"❌ query_selector_all failed: {e}")
        
        try:
            # Method 3: find_element (if it exists)
            element = await page.find_element("input[name='custname']")
            if element:
                logger.info("✅ find_element works")
            else:
                logger.info("❌ find_element returned None")
        except Exception as e:
            logger.error(f"❌ find_element failed: {e}")
        
        # Check element object methods if we found one
        try:
            element = await page.query_selector("input[name='custname']")
            if element:
                logger.info(f"🔍 Element object type: {type(element)}")
                logger.info(f"🔍 Element methods: {[method for method in dir(element) if not method.startswith('_')]}")
        except Exception as e:
            logger.error(f"❌ Element inspection failed: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

async def main():
    """Run API test"""
    logger.info("🚀 Starting Zendriver API test...")
    success = await test_zendriver_api()
    
    if success:
        logger.info("🎉 API test completed successfully!")
    else:
        logger.error("❌ API test failed!")

if __name__ == '__main__':
    asyncio.run(main())

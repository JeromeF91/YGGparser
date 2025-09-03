#!/usr/bin/env python3
"""
Manual authentication script for YGG Torrent
Use this when Cloudflare challenges require human interaction
"""

import asyncio
import logging
import json
from datetime import datetime
from pathlib import Path

import zendriver as zd
import cloudscraper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create necessary directories
Path("data").mkdir(exist_ok=True)

async def manual_authentication():
    """Manual authentication with human interaction for Cloudflare challenges"""
    try:
        logger.info("🚀 Starting manual authentication...")
        logger.info("💡 This will open a browser window where you can manually complete the Cloudflare challenge")
        
        # Start browser in non-headless mode for manual interaction
        browser = await zd.start(
            headless=False,  # Show browser window
            disable_images=False,  # Keep images for better UX
            disable_javascript=False,  # Keep JS enabled for Cloudflare
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Navigate to login page
        logger.info("🌐 Navigating to YGG Torrent login page...")
        page = await browser.get("https://www.yggtorrent.top/auth/login")
        
        # Wait for user to complete Cloudflare challenge
        logger.info("🛡️ Please complete the Cloudflare challenge in the browser window...")
        logger.info("⏳ Waiting for you to complete the challenge...")
        
        # Wait for the page to change (challenge completed)
        max_wait = 300  # 5 minutes max wait
        wait_time = 0
        
        while wait_time < max_wait:
            await asyncio.sleep(5)
            wait_time += 5
            
            try:
                current_url = await page.get_url()
                page_title = await page.get_title()
                page_content = await page.get_content()
                
                # Check if we're past the Cloudflare challenge
                if ("just a moment" not in page_content.lower() and 
                    "verify you are human" not in page_content.lower() and
                    "cloudflare" not in page_content.lower()):
                    
                    logger.info("✅ Cloudflare challenge appears to be completed!")
                    logger.info(f"📍 Current URL: {current_url}")
                    logger.info(f"📄 Page title: {page_title}")
                    
                    # Try to find login form
                    username_field = await page.select("input[name='id']")
                    if not username_field:
                        username_field = await page.select("input[type='text']")
                    
                    if username_field:
                        logger.info("✅ Login form found! Please enter your credentials manually in the browser...")
                        logger.info("⏳ Waiting for you to complete login...")
                        
                        # Wait for login to complete
                        login_wait = 0
                        max_login_wait = 300  # 5 minutes for login
                        
                        while login_wait < max_login_wait:
                            await asyncio.sleep(5)
                            login_wait += 5
                            
                            current_url = await page.get_url()
                            page_title = await page.get_title()
                            
                            # Check if login was successful
                            if "login" not in current_url.lower() and "yggtorrent" in page_title.lower():
                                logger.info("✅ Login successful!")
                                
                                # Extract cookies
                                cookies = await page.get_cookies()
                                logger.info(f"🍪 Extracted {len(cookies)} cookies")
                                
                                # Convert cookies to format usable by cloudscraper
                                cookie_dict = {}
                                for cookie in cookies:
                                    cookie_dict[cookie['name']] = cookie['value']
                                
                                # Save cookies to file
                                cookie_file = f"data/manual_cookies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                                with open(cookie_file, 'w') as f:
                                    json.dump(cookie_dict, f, indent=2)
                                logger.info(f"💾 Cookies saved to: {cookie_file}")
                                
                                # Test with cloudscraper
                                logger.info("🧪 Testing cookies with cloudscraper...")
                                scraper = cloudscraper.create_scraper()
                                scraper.cookies.update(cookie_dict)
                                
                                response = scraper.get("https://www.yggtorrent.top/rss")
                                if response.status_code == 200:
                                    logger.info("✅ Cookies work with cloudscraper!")
                                    logger.info("🎉 Manual authentication completed successfully!")
                                    return True
                                else:
                                    logger.error(f"❌ Cookies test failed: {response.status_code}")
                                    return False
                        
                        logger.error("❌ Login timeout - please try again")
                        return False
                    else:
                        logger.error("❌ Login form not found after challenge completion")
                        return False
                
                logger.info(f"⏳ Still waiting for challenge completion... ({wait_time}s/{max_wait}s)")
                
            except Exception as e:
                logger.error(f"❌ Error checking page status: {e}")
                continue
        
        logger.error("❌ Timeout waiting for Cloudflare challenge completion")
        return False
        
    except Exception as e:
        logger.error(f"❌ Manual authentication failed: {e}")
        return False

async def main():
    """Main function"""
    logger.info("🔧 YGG Torrent Manual Authentication Tool")
    logger.info("=" * 50)
    logger.info("This tool will help you manually complete Cloudflare challenges")
    logger.info("A browser window will open where you can:")
    logger.info("1. Complete the Cloudflare challenge")
    logger.info("2. Enter your login credentials")
    logger.info("3. The tool will extract cookies for API use")
    logger.info("=" * 50)
    
    success = await manual_authentication()
    
    if success:
        logger.info("🎉 Manual authentication completed successfully!")
        logger.info("💡 You can now use the extracted cookies with the API")
    else:
        logger.error("❌ Manual authentication failed")

if __name__ == '__main__':
    asyncio.run(main())

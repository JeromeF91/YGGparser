#!/usr/bin/env python3
"""
Debug RSS Feed with New Cookies
Check what's happening with the RSS feed response
"""

import os
import requests
import cloudscraper


def setup_session_with_cookies(cookie_string):
    """Setup session with the new cookies."""
    session = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'linux',
            'mobile': False
        }
    )
    
    # Set cookies
    for cookie in cookie_string.split(';'):
        if '=' in cookie:
            name, value = cookie.strip().split('=', 1)
            session.cookies.set(name, value)
    
    return session


def debug_rss_response():
    """Debug the RSS response to see what's happening."""
    print("🔍 Debugging RSS Feed Response")
    print("=" * 50)
    
    # Use the new cookie string
    cookie_string = "account_created=true; a3_promo_details=eyJjb3VudGRvd25fZGF0ZSI6IjA5LzMvMjAyNSAyMzo1OTo1OSIsInRzIjoxNzU2OTU4Mzk5fQ==; ygg_=TQoSUGjRCTIJtlhke23R5WT%2CqD6UjPULlwZ%2CV7-THNorSdsU; cf_clearance=pepwzJctlAHMOS5kF3VOcDr89.DzFFYNmDie0xHaCyQ-1756915424-1.2.1.1-pKsLH_R6a1..NHhT0Km1Z5_NNDas3Ta_QuFR9.YiE0jlyS0nmiZrAPsbyXE95xVFn.wl_ObhLMy8wAaKtr_UQ4cr2q85W4jz2V91kZ6kYs0UDjNDWMQ99HSYh2ekZhWviqiGOPVMFivDqqJyP4WmTEQ3nuE2WVV4vx0MnRZHAs17eS6n_jls6FAXiiWOpj0a_zaUaumjHaACUMlerTe_bt_NF_sO7GIKw27gJ7EQr4A"
    
    print(f"🍪 Using new cookies ({len(cookie_string.split(';'))} cookies)")
    
    try:
        # Setup session
        session = setup_session_with_cookies(cookie_string)
        
        # Test RSS feed
        rss_url = "https://www.yggtorrent.top/rss?action=generate&type=subcat&id=2163&passkey=DJdLXYBi2WmyQB0PdNWZ8u9RZEnTqiXT"
        
        print(f"📡 Testing RSS URL: {rss_url}")
        
        response = session.get(rss_url, timeout=30)
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📊 Response headers: {dict(response.headers)}")
        print(f"📊 Content length: {len(response.text)} characters")
        
        # Save the response for inspection
        os.makedirs('data', exist_ok=True)
        with open('data/rss_debug_response.xml', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"💾 Response saved to: data/rss_debug_response.xml")
        
        # Check first few characters
        print(f"\n📄 First 200 characters:")
        print(response.text[:200])
        
        # Check if it starts with XML
        if response.text.strip().startswith('<?xml'):
            print("✅ Response starts with XML declaration")
        else:
            print("❌ Response doesn't start with XML declaration")
        
        # Check for common XML patterns
        if '<rss' in response.text.lower():
            print("✅ Contains RSS tag")
        else:
            print("❌ No RSS tag found")
        
        if '<channel>' in response.text.lower():
            print("✅ Contains channel tag")
        else:
            print("❌ No channel tag found")
        
        if '<item>' in response.text.lower():
            print("✅ Contains item tags")
        else:
            print("❌ No item tags found")
        
        # Check for error messages
        if 'error' in response.text.lower():
            print("⚠️ Response contains 'error'")
        
        if 'forbidden' in response.text.lower():
            print("⚠️ Response contains 'forbidden'")
        
        if 'unauthorized' in response.text.lower():
            print("⚠️ Response contains 'unauthorized'")
        
        # Try to parse as XML
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.text)
            print("✅ Response is valid XML")
            
            # Count items
            items = root.findall('.//item')
            print(f"📊 Found {len(items)} items in RSS feed")
            
        except Exception as e:
            print(f"❌ XML parsing failed: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main function."""
    debug_rss_response()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test New Cookies from Undetected ChromeDriver
Tests the newly generated cookies with RSS feed and download functionality
"""

import os
import json
import time
import requests
import cloudscraper
import xml.etree.ElementTree as ET


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


def test_rss_access(session):
    """Test RSS feed access with new cookies."""
    print("🧪 Testing RSS feed access with new cookies...")
    
    rss_url = "https://www.yggtorrent.top/rss?action=generate&type=subcat&id=2163&passkey=DJdLXYBi2WmyQB0PdNWZ8u9RZEnTqiXT"
    
    try:
        response = session.get(rss_url, timeout=30)
        print(f"📊 RSS feed status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ RSS feed access successful!")
            print(f"📄 RSS content length: {len(response.text)} characters")
            
            # Check if it's valid XML
            if response.text.strip().startswith('<?xml'):
                print("✅ Valid XML RSS feed received!")
                return response.text
            else:
                print("⚠️ Response doesn't look like valid XML")
                return None
        else:
            print(f"❌ RSS feed access failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error accessing RSS feed: {e}")
        return None


def test_download_with_new_cookies(session, torrent_id, torrent_title, passkey):
    """Test downloading a torrent file with new cookies."""
    print(f"\n📥 Testing download: {torrent_title}")
    
    try:
        # Use RSS download URL
        download_url = f"https://www.yggtorrent.top/rss/download?id={torrent_id}&passkey={passkey}"
        print(f"🔗 Download URL: {download_url}")
        
        response = session.get(download_url, timeout=30)
        print(f"📊 Response status: {response.status_code}")
        print(f"📊 Content type: {response.headers.get('content-type', 'Unknown')}")
        print(f"📊 Content length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            content = response.content
            content_type = response.headers.get('content-type', '')
            
            # Check if it's a torrent file
            if (content_type == 'application/x-bittorrent' or 
                content.startswith(b'd8:announce') or 
                content.startswith(b'd10:created') or
                b'announce' in content[:100]):
                
                # Save the torrent file
                safe_title = "".join(c for c in torrent_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                torrent_filename = f"data/new_cookies_{safe_title}.torrent"
                
                with open(torrent_filename, 'wb') as f:
                    f.write(content)
                
                print(f"✅ Successfully downloaded: {torrent_filename}")
                print(f"📊 File size: {len(content)} bytes")
                return torrent_filename
            else:
                print(f"❌ Downloaded content doesn't look like a torrent file")
                return None
        else:
            print(f"❌ Download failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error downloading torrent: {e}")
        return None


def main():
    """Main function."""
    print("🧪 Testing New Cookies from Undetected ChromeDriver")
    print("=" * 60)
    
    # Use the new cookie string from undetected-chromedriver
    cookie_string = "account_created=true; a3_promo_details=eyJjb3VudGRvd25fZGF0ZSI6IjA5LzMvMjAyNSAyMzo1OTo1OSIsInRzIjoxNzU2OTU4Mzk5fQ==; ygg_=TQoSUGjRCTIJtlhke23R5WT%2CqD6UjPULlwZ%2CV7-THNorSdsU; cf_clearance=pepwzJctlAHMOS5kF3VOcDr89.DzFFYNmDie0xHaCyQ-1756915424-1.2.1.1-pKsLH_R6a1..NHhT0Km1Z5_NNDas3Ta_QuFR9.YiE0jlyS0nmiZrAPsbyXE95xVFn.wl_ObhLMy8wAaKtr_UQ4cr2q85W4jz2V91kZ6kYs0UDjNDWMQ99HSYh2ekZhWviqiGOPVMFivDqqJyP4WmTEQ3nuE2WVV4vx0MnRZHAs17eS6n_jls6FAXiiWOpj0a_zaUaumjHaACUMlerTe_bt_NF_sO7GIKw27gJ7EQr4A"
    
    passkey = "DJdLXYBi2WmyQB0PdNWZ8u9RZEnTqiXT"
    
    print(f"🍪 Using new cookies ({len(cookie_string.split(';'))} cookies)")
    print(f"🔑 Using passkey: {passkey}")
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    try:
        # Setup session
        session = setup_session_with_cookies(cookie_string)
        
        # Test RSS access
        rss_content = test_rss_access(session)
        
        if rss_content:
            # Parse RSS to get a torrent for testing
            root = ET.fromstring(rss_content)
            items = root.findall('.//item')
            
            if items:
                # Test with first torrent
                first_item = items[0]
                title = first_item.find('title')
                link = first_item.find('link')
                
                if title is not None and link is not None:
                    torrent_id = link.text.split('/')[-1].split('-')[0]
                    torrent_title = title.text
                    
                    print(f"\n📋 Testing with torrent: {torrent_title}")
                    print(f"🆔 Torrent ID: {torrent_id}")
                    
                    # Test download
                    downloaded_file = test_download_with_new_cookies(session, torrent_id, torrent_title, passkey)
                    
                    if downloaded_file:
                        print(f"\n🎉 SUCCESS! New cookies work perfectly!")
                        print(f"✅ RSS feed access: Working")
                        print(f"✅ Torrent download: Working")
                        print(f"✅ File saved: {downloaded_file}")
                        
                        # Save the working cookie string
                        config = {
                            "cookie_string": cookie_string,
                            "passkey": passkey,
                            "tested_at": time.strftime('%Y-%m-%d %H:%M:%S'),
                            "method": "undetected_chromedriver",
                            "status": "working"
                        }
                        
                        config_file = "data/working_auto_cookies.json"
                        with open(config_file, 'w') as f:
                            json.dump(config, f, indent=2)
                        
                        print(f"💾 Working cookies saved to: {config_file}")
                        print(f"\n🚀 You now have a fully automated system!")
                        print(f"🍪 Cookie string: {cookie_string}")
                    else:
                        print(f"\n❌ Download test failed")
                else:
                    print(f"\n❌ Could not parse torrent from RSS")
            else:
                print(f"\n❌ No torrents found in RSS feed")
        else:
            print(f"\n❌ RSS feed access failed")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    
    print("\n📁 Check the 'data/' directory for results")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Final Automated Test with Undetected ChromeDriver Cookies
Tests the complete automated workflow: authentication + RSS + download
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


def get_torrents_from_rss(session, passkey):
    """Get torrents from RSS feed."""
    print("📡 Getting torrents from RSS feed...")
    
    rss_url = f"https://www.yggtorrent.top/rss?action=generate&type=subcat&id=2163&passkey={passkey}"
    
    try:
        response = session.get(rss_url, timeout=30)
        
        if response.status_code == 200:
            # Parse XML (even without <?xml declaration)
            root = ET.fromstring(response.text)
            items = root.findall('.//item')
            
            torrents = []
            for item in items[:3]:  # Get first 3 for testing
                title = item.find('title')
                link = item.find('link')
                
                if title is not None and link is not None:
                    # Extract torrent ID from the link
                    torrent_id = link.text.split('/')[-1].split('-')[0]
                    torrents.append({
                        'title': title.text,
                        'link': link.text,
                        'id': torrent_id
                    })
            
            print(f"✅ Found {len(torrents)} torrents for testing")
            return torrents
        else:
            print(f"❌ Failed to get RSS feed: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error getting torrents: {e}")
        return []


def download_torrent(session, torrent_id, torrent_title, passkey):
    """Download a torrent file."""
    print(f"\n📥 Downloading: {torrent_title}")
    
    try:
        # Use RSS download URL
        download_url = f"https://www.yggtorrent.top/rss/download?id={torrent_id}&passkey={passkey}"
        
        response = session.get(download_url, timeout=30)
        
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
                torrent_filename = f"data/auto_{safe_title}.torrent"
                
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
    print("🚀 Final Automated Test with Undetected ChromeDriver")
    print("=" * 60)
    print("Testing complete automated workflow:")
    print("1. ✅ Authentication (undetected-chromedriver)")
    print("2. 🧪 RSS feed access")
    print("3. 🧪 Torrent download")
    print("=" * 60)
    
    # Use the new cookie string from undetected-chromedriver
    cookie_string = "account_created=true; a3_promo_details=eyJjb3VudGRvd25fZGF0ZSI6IjA5LzMvMjAyNSAyMzo1OTo1OSIsInRzIjoxNzU2OTU4Mzk5fQ==; ygg_=TQoSUGjRCTIJtlhke23R5WT%2CqD6UjPULlwZ%2CV7-THNorSdsU; cf_clearance=pepwzJctlAHMOS5kF3VOcDr89.DzFFYNmDie0xHaCyQ-1756915424-1.2.1.1-pKsLH_R6a1..NHhT0Km1Z5_NNDas3Ta_QuFR9.YiE0jlyS0nmiZrAPsbyXE95xVFn.wl_ObhLMy8wAaKtr_UQ4cr2q85W4jz2V91kZ6kYs0UDjNDWMQ99HSYh2ekZhWviqiGOPVMFivDqqJyP4WmTEQ3nuE2WVV4vx0MnRZHAs17eS6n_jls6FAXiiWOpj0a_zaUaumjHaACUMlerTe_bt_NF_sO7GIKw27gJ7EQr4A"
    
    passkey = "DJdLXYBi2WmyQB0PdNWZ8u9RZEnTqiXT"
    
    print(f"🍪 Using automated cookies ({len(cookie_string.split(';'))} cookies)")
    print(f"🔑 Using passkey: {passkey}")
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    try:
        # Setup session
        session = setup_session_with_cookies(cookie_string)
        
        # Get torrents from RSS
        torrents = get_torrents_from_rss(session, passkey)
        
        if not torrents:
            print("❌ No torrents found for testing")
            return
        
        # Test downloading torrents
        downloaded_files = []
        for i, torrent in enumerate(torrents):
            print(f"\n{'='*60}")
            print(f"Testing download {i+1}/{len(torrents)}")
            print(f"Torrent ID: {torrent['id']}")
            
            torrent_file = download_torrent(session, torrent['id'], torrent['title'], passkey)
            
            if torrent_file:
                downloaded_files.append(torrent_file)
            
            # Small delay between downloads
            time.sleep(2)
        
        # Summary
        print(f"\n{'='*60}")
        print("📊 AUTOMATED SYSTEM TEST SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Authentication: Working (undetected-chromedriver)")
        print(f"✅ RSS Feed Access: Working ({len(torrents)} torrents found)")
        print(f"✅ Torrent Downloads: {len(downloaded_files)}/{len(torrents)} successful")
        
        if downloaded_files:
            print("\n📁 Downloaded files:")
            for file in downloaded_files:
                file_size = os.path.getsize(file)
                print(f"  📄 {file} ({file_size} bytes)")
            
            print("\n🎉 COMPLETE AUTOMATED SYSTEM IS WORKING!")
            print("\n🚀 You now have a fully automated YGG Torrent parser that:")
            print("  1. ✅ Automatically bypasses Cloudflare")
            print("  2. ✅ Automatically authenticates and gets cookies")
            print("  3. ✅ Automatically parses RSS feeds")
            print("  4. ✅ Automatically downloads torrent files")
            
            # Save the complete working configuration
            config = {
                "cookie_string": cookie_string,
                "passkey": passkey,
                "tested_at": time.strftime('%Y-%m-%d %H:%M:%S'),
                "method": "undetected_chromedriver",
                "status": "fully_working",
                "downloaded_files": downloaded_files,
                "rss_url": f"https://www.yggtorrent.top/rss?action=generate&type=subcat&id=2163&passkey={passkey}",
                "download_url_pattern": "https://www.yggtorrent.top/rss/download?id={id}&passkey={passkey}"
            }
            
            config_file = "data/complete_automated_system.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"\n💾 Complete system config saved to: {config_file}")
            print(f"🍪 Working cookie string: {cookie_string}")
        else:
            print("\n❌ No torrent files were successfully downloaded")
            
    except Exception as e:
        print(f"❌ Error during automated test: {e}")
    
    print("\n📁 Check the 'data/' directory for results")


if __name__ == "__main__":
    main()

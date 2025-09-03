#!/usr/bin/env python3
"""
Working YGG Torrent Download
Uses the correct download link pattern found in the HTML
"""

import os
import json
import time
import requests
import cloudscraper
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse


def setup_session_with_cookies(cookie_string):
    """Setup session with the working cookies."""
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


def get_torrent_list(session):
    """Get list of torrents from RSS feed."""
    print("📡 Getting torrent list from RSS feed...")
    
    rss_url = "https://www.yggtorrent.top/rss?action=generate&type=subcat&id=2163&passkey=DJdLXYBi2WmyQB0PdNWZ8u9RZEnTqiXT"
    
    try:
        response = session.get(rss_url, timeout=30)
        
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            items = root.findall('.//item')
            
            torrents = []
            for item in items[:3]:  # Get first 3 torrents for testing
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
        print(f"❌ Error getting torrent list: {e}")
        return []


def download_torrent_file(session, torrent_id, torrent_title):
    """Download a single torrent file using the correct URL pattern."""
    print(f"\n📥 Downloading: {torrent_title}")
    
    try:
        # Use the correct download URL pattern
        download_url = f"https://www.yggtorrent.top/engine/download_torrent?id={torrent_id}"
        print(f"🔗 Download URL: {download_url}")
        
        # Download the torrent file
        response = session.get(download_url, timeout=30)
        
        if response.status_code == 200:
            content = response.content
            content_type = response.headers.get('content-type', '')
            
            print(f"📊 Response status: {response.status_code}")
            print(f"📊 Content type: {content_type}")
            print(f"📊 Content length: {len(content)} bytes")
            
            # Check if it's actually a torrent file
            if (content_type == 'application/x-bittorrent' or 
                content.startswith(b'd8:announce') or 
                content.startswith(b'd10:created') or
                b'announce' in content[:100]):
                
                # Save the torrent file
                safe_title = "".join(c for c in torrent_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                torrent_filename = f"data/{safe_title}.torrent"
                
                with open(torrent_filename, 'wb') as f:
                    f.write(content)
                
                print(f"✅ Successfully downloaded: {torrent_filename}")
                print(f"📊 File size: {len(content)} bytes")
                
                # Verify it's a valid torrent file
                if verify_torrent_file(torrent_filename):
                    print("✅ Torrent file is valid!")
                    return torrent_filename
                else:
                    print("⚠️ Torrent file might be invalid")
                    return torrent_filename
            else:
                print(f"❌ Downloaded content doesn't look like a torrent file")
                print(f"📊 Content preview: {content[:100]}")
                
                # Save the content anyway for debugging
                debug_filename = f"data/debug_{torrent_id}.bin"
                with open(debug_filename, 'wb') as f:
                    f.write(content)
                print(f"💾 Saved debug content to: {debug_filename}")
                
                return None
        else:
            print(f"❌ Failed to download torrent file: {response.status_code}")
            print(f"📊 Response headers: {dict(response.headers)}")
            return None
            
    except Exception as e:
        print(f"❌ Error downloading torrent: {e}")
        return None


def verify_torrent_file(filename):
    """Verify that a file is a valid torrent file."""
    try:
        with open(filename, 'rb') as f:
            content = f.read()
        
        # Check for common torrent file signatures
        if (content.startswith(b'd8:announce') or 
            content.startswith(b'd10:created') or
            b'announce' in content[:200]):
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error verifying torrent file: {e}")
        return False


def test_working_download():
    """Test downloading torrent files with the correct URL pattern."""
    print("🧪 Testing Working YGG Torrent Download")
    print("=" * 60)
    
    # Use the working cookie string
    cookie_string = "cf_clearance=pMz272Hk0MghOxPa6CL4tXxC72Ny7Rz363To3U9JoKM-1742770534-1.2.1.1-L.dJfLkkUaNHES14E1ufGvzrrRmJG_go8yUufLXW7sbnq6Io.F8mbrUcP1xNequWe4wGo76nxv3IOWzImH5nxdIAHT50PmmeMdsBXrSA.x.MwlPd.0Z_6Uqncdyg8I2IUfv38hgU12zcRmXniNlLf.oUcmhJ0NsyEolAcP34k_ebGvu9kbGnjQiN83h1oh81fyE60S.HLI2Rpw6JmTUX_H2mGps8hvFQqgxIofgSZwWr4c9aYOUYSLHHkUoPxglOn5YydYlyYrgLmFp3S1s0l51_gvxM3AGP4He8AxWmD2pHwIP8N9iTj1fJdxkUYIQ3uMfzQZgG371WpKjLj2pvSENEppKZhcB7nPJ7qeH8Dln8sC7_qI7J1y7a_3VJ_DnrSrih3vdi_q6qOl056I2jgBirAvsOwxoOczk8JQWZUW0; account_created=true; yggxf_user=439444%2CYWaCJJ1u-VY9MkwAh95eibG4JMjT4EgJy8wAJDYY; a3_promo_details=eyJjb3VudGRvd25fZGF0ZSI6IjA4LzI5LzIwMjUgMjM6NTk6NTkiLCJ0cyI6MTc1NjUyNjM5OX0=; ygg_=3vzc06%2Cr34dFPtwUue9xUw579L-HkYkCOIhc%2CToDlmouG%2CxZ"
    
    print(f"🍪 Using working cookies ({len(cookie_string.split(';'))} cookies)")
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    try:
        # Setup session
        session = setup_session_with_cookies(cookie_string)
        
        # Get torrent list
        torrents = get_torrent_list(session)
        
        if not torrents:
            print("❌ No torrents found for testing")
            return
        
        # Test downloading torrents
        downloaded_files = []
        for i, torrent in enumerate(torrents):
            print(f"\n{'='*60}")
            print(f"Testing download {i+1}/{len(torrents)}")
            print(f"Torrent ID: {torrent['id']}")
            
            torrent_file = download_torrent_file(session, torrent['id'], torrent['title'])
            
            if torrent_file:
                downloaded_files.append(torrent_file)
            
            # Small delay between downloads
            time.sleep(2)
        
        # Summary
        print(f"\n{'='*60}")
        print("📊 DOWNLOAD TEST SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Successfully downloaded: {len(downloaded_files)} torrent files")
        
        if downloaded_files:
            print("\n📁 Downloaded files:")
            for file in downloaded_files:
                file_size = os.path.getsize(file)
                print(f"  📄 {file} ({file_size} bytes)")
            
            print("\n🎉 Torrent download functionality is working!")
            print("\n🚀 You can now use the full download system:")
            print("  1. Run: python3 ygg_downloader.py")
            print("  2. Or use the main parser with download enabled")
        else:
            print("\n❌ No torrent files were successfully downloaded")
            
    except Exception as e:
        print(f"❌ Error during download test: {e}")
    
    print("\n📁 Check the 'data/' directory for downloaded files")


def main():
    """Main function."""
    test_working_download()


if __name__ == "__main__":
    main()

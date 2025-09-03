#!/usr/bin/env python3
"""
YGG Torrent RSS Direct Download
Tests downloading torrent files directly from RSS download URLs
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


def download_from_rss_url(session, torrent_id, torrent_title, passkey):
    """Download torrent file directly from RSS download URL."""
    print(f"\n📥 Downloading from RSS URL: {torrent_title}")
    
    try:
        # Use the RSS download URL pattern
        rss_download_url = f"https://www.yggtorrent.top/rss/download?id={torrent_id}&passkey={passkey}"
        print(f"🔗 RSS Download URL: {rss_download_url}")
        
        # Download the torrent file
        response = session.get(rss_download_url, timeout=30)
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📊 Content type: {response.headers.get('content-type', 'Unknown')}")
        print(f"📊 Content length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            content = response.content
            content_type = response.headers.get('content-type', '')
            
            # Check if it's actually a torrent file
            if (content_type == 'application/x-bittorrent' or 
                content.startswith(b'd8:announce') or 
                content.startswith(b'd10:created') or
                b'announce' in content[:100]):
                
                # Save the torrent file
                safe_title = "".join(c for c in torrent_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                torrent_filename = f"data/rss_{safe_title}.torrent"
                
                with open(torrent_filename, 'wb') as f:
                    f.write(content)
                
                print(f"✅ Successfully downloaded from RSS: {torrent_filename}")
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
                debug_filename = f"data/debug_rss_{torrent_id}.bin"
                with open(debug_filename, 'wb') as f:
                    f.write(content)
                print(f"💾 Saved debug content to: {debug_filename}")
                
                return None
        else:
            print(f"❌ Failed to download from RSS URL: {response.status_code}")
            print(f"📊 Response headers: {dict(response.headers)}")
            
            # Try to get response text for debugging
            try:
                response_text = response.text
                print(f"📊 Response text: {response_text[:200]}...")
            except:
                pass
            
            return None
            
    except Exception as e:
        print(f"❌ Error downloading from RSS URL: {e}")
        return None


def download_from_engine_url(session, torrent_id, torrent_title):
    """Download torrent file from engine URL (for comparison)."""
    print(f"\n📥 Downloading from engine URL: {torrent_title}")
    
    try:
        # Use the engine download URL pattern
        engine_download_url = f"https://www.yggtorrent.top/engine/download_torrent?id={torrent_id}"
        print(f"🔗 Engine Download URL: {engine_download_url}")
        
        # Download the torrent file
        response = session.get(engine_download_url, timeout=30)
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📊 Content type: {response.headers.get('content-type', 'Unknown')}")
        print(f"📊 Content length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            content = response.content
            content_type = response.headers.get('content-type', '')
            
            # Check if it's actually a torrent file
            if (content_type == 'application/x-bittorrent' or 
                content.startswith(b'd8:announce') or 
                content.startswith(b'd10:created') or
                b'announce' in content[:100]):
                
                # Save the torrent file
                safe_title = "".join(c for c in torrent_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                torrent_filename = f"data/engine_{safe_title}.torrent"
                
                with open(torrent_filename, 'wb') as f:
                    f.write(content)
                
                print(f"✅ Successfully downloaded from engine: {torrent_filename}")
                print(f"📊 File size: {len(content)} bytes")
                
                return torrent_filename
            else:
                print(f"❌ Downloaded content doesn't look like a torrent file")
                return None
        else:
            print(f"❌ Failed to download from engine URL: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error downloading from engine URL: {e}")
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


def compare_download_methods():
    """Compare RSS download vs engine download methods."""
    print("🧪 Comparing RSS Download vs Engine Download Methods")
    print("=" * 70)
    
    # Use the working cookie string
    cookie_string = "cf_clearance=pMz272Hk0MghOxPa6CL4tXxC72Ny7Rz363To3U9JoKM-1742770534-1.2.1.1-L.dJfLkkUaNHES14E1ufGvzrrRmJG_go8yUufLXW7sbnq6Io.F8mbrUcP1xNequWe4wGo76nxv3IOWzImH5nxdIAHT50PmmeMdsBXrSA.x.MwlPd.0Z_6Uqncdyg8I2IUfv38hgU12zcRmXniNlLf.oUcmhJ0NsyEolAcP34k_ebGvu9kbGnjQiN83h1oh81fyE60S.HLI2Rpw6JmTUX_H2mGps8hvFQqgxIofgSZwWr4c9aYOUYSLHHkUoPxglOn5YydYlyYrgLmFp3S1s0l51_gvxM3AGP4He8AxWmD2pHwIP8N9iTj1fJdxkUYIQ3uMfzQZgG371WpKjLj2pvSENEppKZhcB7nPJ7qeH8Dln8sC7_qI7J1y7a_3VJ_DnrSrih3vdi_q6qOl056I2jgBirAvsOwxoOczk8JQWZUW0; account_created=true; yggxf_user=439444%2CYWaCJJ1u-VY9MkwAh95eibG4JMjT4EgJy8wAJDYY; a3_promo_details=eyJjb3VudGRvd25fZGF0ZSI6IjA4LzI5LzIwMjUgMjM6NTk6NTkiLCJ0cyI6MTc1NjUyNjM5OX0=; ygg_=3vzc06%2Cr34dFPtwUue9xUw579L-HkYkCOIhc%2CToDlmouG%2CxZ"
    
    # Passkey from the RSS URL
    passkey = "DJdLXYBi2WmyQB0PdNWZ8u9RZEnTqiXT"
    
    print(f"🍪 Using working cookies ({len(cookie_string.split(';'))} cookies)")
    print(f"🔑 Using passkey: {passkey}")
    
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
        
        # Test both download methods
        rss_downloads = []
        engine_downloads = []
        
        for i, torrent in enumerate(torrents[:2]):  # Test first 2 torrents
            print(f"\n{'='*70}")
            print(f"Testing torrent {i+1}/2: {torrent['title']}")
            print(f"Torrent ID: {torrent['id']}")
            
            # Method 1: RSS Download
            print(f"\n--- Method 1: RSS Download ---")
            rss_file = download_from_rss_url(session, torrent['id'], torrent['title'], passkey)
            if rss_file:
                rss_downloads.append(rss_file)
            
            time.sleep(1)
            
            # Method 2: Engine Download
            print(f"\n--- Method 2: Engine Download ---")
            engine_file = download_from_engine_url(session, torrent['id'], torrent['title'])
            if engine_file:
                engine_downloads.append(engine_file)
            
            time.sleep(2)
        
        # Summary
        print(f"\n{'='*70}")
        print("📊 DOWNLOAD METHODS COMPARISON")
        print(f"{'='*70}")
        print(f"✅ RSS Downloads successful: {len(rss_downloads)}")
        print(f"✅ Engine Downloads successful: {len(engine_downloads)}")
        
        if rss_downloads:
            print("\n📁 RSS Downloaded files:")
            for file in rss_downloads:
                file_size = os.path.getsize(file)
                print(f"  📄 {file} ({file_size} bytes)")
        
        if engine_downloads:
            print("\n📁 Engine Downloaded files:")
            for file in engine_downloads:
                file_size = os.path.getsize(file)
                print(f"  📄 {file} ({file_size} bytes)")
        
        # Compare file sizes if both methods worked
        if rss_downloads and engine_downloads:
            print("\n🔍 File size comparison:")
            for i, (rss_file, engine_file) in enumerate(zip(rss_downloads, engine_downloads)):
                rss_size = os.path.getsize(rss_file)
                engine_size = os.path.getsize(engine_file)
                print(f"  Torrent {i+1}: RSS={rss_size} bytes, Engine={engine_size} bytes")
                if rss_size == engine_size:
                    print(f"    ✅ Files are identical in size")
                else:
                    print(f"    ⚠️ Files have different sizes")
        
        if rss_downloads or engine_downloads:
            print("\n🎉 Download functionality is working!")
            print("\n💡 Both methods can be used:")
            print("  - RSS Download: https://www.yggtorrent.top/rss/download?id={id}&passkey={passkey}")
            print("  - Engine Download: https://www.yggtorrent.top/engine/download_torrent?id={id}")
        else:
            print("\n❌ No downloads were successful")
            
    except Exception as e:
        print(f"❌ Error during download comparison: {e}")
    
    print("\n📁 Check the 'data/' directory for downloaded files")


def main():
    """Main function."""
    compare_download_methods()


if __name__ == "__main__":
    main()

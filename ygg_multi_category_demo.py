#!/usr/bin/env python3
"""
YGG Torrent Multi-Category Demo
Download samples from different categories to demonstrate variety
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


def download_sample_from_category(session, category_id, category_name, passkey):
    """Download a sample torrent from a category."""
    print(f"\n📥 Downloading sample from: {category_name}")
    
    rss_url = f"https://www.yggtorrent.top/rss?action=generate&type=subcat&id={category_id}&passkey={passkey}"
    
    try:
        response = session.get(rss_url, timeout=30)
        
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            items = root.findall('.//item')
            
            if items:
                # Get first item
                first_item = items[0]
                title = first_item.find('title')
                link = first_item.find('link')
                
                if title is not None and link is not None:
                    torrent_id = link.text.split('/')[-1].split('-')[0]
                    torrent_title = title.text
                    
                    print(f"  📋 Torrent: {torrent_title}")
                    print(f"  🆔 ID: {torrent_id}")
                    
                    # Download the torrent
                    download_url = f"https://www.yggtorrent.top/rss/download?id={torrent_id}&passkey={passkey}"
                    
                    download_response = session.get(download_url, timeout=30)
                    
                    if download_response.status_code == 200:
                        content = download_response.content
                        
                        # Check if it's a torrent file
                        if (content.startswith(b'd8:announce') or 
                            content.startswith(b'd10:created') or
                            b'announce' in content[:100]):
                            
                            # Save the torrent file
                            safe_title = "".join(c for c in torrent_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                            torrent_filename = f"data/multi_{category_name}_{safe_title}.torrent"
                            
                            with open(torrent_filename, 'wb') as f:
                                f.write(content)
                            
                            print(f"  ✅ Downloaded: {torrent_filename}")
                            print(f"  📊 File size: {len(content)} bytes")
                            return torrent_filename
                        else:
                            print(f"  ❌ Downloaded content doesn't look like a torrent file")
                            return None
                    else:
                        print(f"  ❌ Download failed: {download_response.status_code}")
                        return None
                else:
                    print(f"  ❌ Could not parse torrent from RSS")
                    return None
            else:
                print(f"  ❌ No torrents found in category")
                return None
        else:
            print(f"  ❌ Failed to get RSS feed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"  ❌ Error downloading from category {category_name}: {e}")
        return None


def main():
    """Main function."""
    print("🚀 YGG Torrent Multi-Category Demo")
    print("=" * 60)
    print("Downloading samples from different categories to show variety")
    print("=" * 60)
    
    # Use the working cookie string
    cookie_string = "account_created=true; a3_promo_details=eyJjb3VudGRvd25fZGF0ZSI6IjA5LzMvMjAyNSAyMzo1OTo1OSIsInRzIjoxNzU2OTU4Mzk5fQ==; ygg_=TQoSUGjRCTIJtlhke23R5WT%2CqD6UjPULlwZ%2CV7-THNorSdsU; cf_clearance=pepwzJctlAHMOS5kF3VOcDr89.DzFFYNmDie0xHaCyQ-1756915424-1.2.1.1-pKsLH_R6a1..NHhT0Km1Z5_NNDas3Ta_QuFR9.YiE0jlyS0nmiZrAPsbyXE95xVFn.wl_ObhLMy8wAaKtr_UQ4cr2q85W4jz2V91kZ6kYs0UDjNDWMQ99HSYh2ekZhWviqiGOPVMFivDqqJyP4WmTEQ3nuE2WVV4vx0MnRZHAs17eS6n_jls6FAXiiWOpj0a_zaUaumjHaACUMlerTe_bt_NF_sO7GIKw27gJ7EQr4A"
    
    passkey = "DJdLXYBi2WmyQB0PdNWZ8u9RZEnTqiXT"
    
    print(f"🍪 Using automated cookies ({len(cookie_string.split(';'))} cookies)")
    print(f"🔑 Using passkey: {passkey}")
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    # Select diverse categories to demonstrate variety
    demo_categories = [
        {"id": 2163, "name": "Nintendo_Switch", "description": "Switch games"},
        {"id": 2164, "name": "PlayStation_5", "description": "PS5 games"},
        {"id": 2147, "name": "Movies_4K", "description": "4K movies"},
        {"id": 2152, "name": "TV_Shows_4K", "description": "4K TV shows"},
        {"id": 2156, "name": "Music_FLAC", "description": "FLAC music"},
        {"id": 2159, "name": "E_books", "description": "E-books"},
        {"id": 2161, "name": "Anime", "description": "Anime content"},
    ]
    
    print(f"\n📋 Selected {len(demo_categories)} diverse categories for demo:")
    for cat in demo_categories:
        print(f"  📁 {cat['name']} - {cat['description']}")
    
    try:
        # Setup session
        session = setup_session_with_cookies(cookie_string)
        
        downloaded_files = []
        
        for i, category in enumerate(demo_categories, 1):
            print(f"\n{'='*60}")
            print(f"Testing category {i}/{len(demo_categories)}: {category['name']}")
            print(f"{'='*60}")
            
            torrent_file = download_sample_from_category(
                session, 
                category["id"], 
                category["name"], 
                passkey
            )
            
            if torrent_file:
                downloaded_files.append({
                    "category": category["name"],
                    "file": torrent_file,
                    "size": os.path.getsize(torrent_file)
                })
            
            # Small delay between downloads
            time.sleep(2)
        
        # Summary
        print(f"\n{'='*60}")
        print("📊 MULTI-CATEGORY DEMO SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Categories tested: {len(demo_categories)}")
        print(f"✅ Successful downloads: {len(downloaded_files)}")
        print(f"❌ Failed downloads: {len(demo_categories) - len(downloaded_files)}")
        
        if downloaded_files:
            print(f"\n📁 Downloaded files:")
            total_size = 0
            for item in downloaded_files:
                print(f"  📄 {item['category']}: {item['file']} ({item['size']} bytes)")
                total_size += item['size']
            
            print(f"\n📊 Total downloaded: {total_size} bytes")
            print(f"📊 Average file size: {total_size // len(downloaded_files)} bytes")
            
            print(f"\n🎉 SUCCESS! Multi-category system is working!")
            print(f"\n🚀 You can now browse and download from any of the 38 categories:")
            print(f"   🎮 Gaming: Nintendo, PlayStation, Xbox, PC")
            print(f"   🎬 Media: Movies, TV Shows, Music")
            print(f"   📚 Books: E-books, Audiobooks")
            print(f"   🎌 Other: Anime, Documentaries")
            
            # Save the demo results
            demo_results = {
                "categories_tested": len(demo_categories),
                "successful_downloads": len(downloaded_files),
                "downloaded_files": downloaded_files,
                "total_size": total_size,
                "tested_at": time.strftime('%Y-%m-%d %H:%M:%S'),
                "method": "undetected_chromedriver",
                "status": "multi_category_working"
            }
            
            results_file = "data/multi_category_demo_results.json"
            with open(results_file, 'w') as f:
                json.dump(demo_results, f, indent=2)
            
            print(f"\n💾 Demo results saved to: {results_file}")
        else:
            print(f"\n❌ No torrent files were successfully downloaded")
            
    except Exception as e:
        print(f"❌ Error during multi-category demo: {e}")
    
    print("\n📁 Check the 'data/' directory for results")


if __name__ == "__main__":
    main()

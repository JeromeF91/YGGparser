#!/usr/bin/env python3
"""
YGG Torrent Category Browser
Browse and test different categories using the automated system
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


def get_category_info():
    """Get information about different categories."""
    categories = {
        # Games
        "nintendo_switch": {"id": 2163, "name": "Nintendo Switch", "description": "Switch games"},
        "nintendo_3ds": {"id": 2162, "name": "Nintendo 3DS", "description": "3DS games"},
        "nintendo_wii_u": {"id": 2161, "name": "Nintendo Wii U", "description": "Wii U games"},
        "nintendo_wii": {"id": 2160, "name": "Nintendo Wii", "description": "Wii games"},
        "nintendo_ds": {"id": 2159, "name": "Nintendo DS", "description": "DS games"},
        "nintendo_gamecube": {"id": 2158, "name": "Nintendo GameCube", "description": "GameCube games"},
        "nintendo_64": {"id": 2157, "name": "Nintendo 64", "description": "N64 games"},
        "nintendo_snes": {"id": 2156, "name": "Super Nintendo", "description": "SNES games"},
        "nintendo_nes": {"id": 2155, "name": "Nintendo NES", "description": "NES games"},
        
        # PlayStation
        "ps5": {"id": 2164, "name": "PlayStation 5", "description": "PS5 games"},
        "ps4": {"id": 2165, "name": "PlayStation 4", "description": "PS4 games"},
        "ps3": {"id": 2166, "name": "PlayStation 3", "description": "PS3 games"},
        "ps2": {"id": 2167, "name": "PlayStation 2", "description": "PS2 games"},
        "ps1": {"id": 2168, "name": "PlayStation 1", "description": "PS1 games"},
        "psp": {"id": 2169, "name": "PlayStation Portable", "description": "PSP games"},
        "ps_vita": {"id": 2170, "name": "PlayStation Vita", "description": "PS Vita games"},
        
        # Xbox
        "xbox_series": {"id": 2171, "name": "Xbox Series X/S", "description": "Xbox Series games"},
        "xbox_one": {"id": 2172, "name": "Xbox One", "description": "Xbox One games"},
        "xbox_360": {"id": 2173, "name": "Xbox 360", "description": "Xbox 360 games"},
        "xbox": {"id": 2174, "name": "Xbox", "description": "Original Xbox games"},
        
        # PC
        "pc_games": {"id": 2145, "name": "PC Games", "description": "PC games"},
        "pc_software": {"id": 2146, "name": "PC Software", "description": "PC software"},
        
        # Movies
        "movies_4k": {"id": 2147, "name": "Movies 4K", "description": "4K movies"},
        "movies_bluray": {"id": 2148, "name": "Movies Blu-ray", "description": "Blu-ray movies"},
        "movies_dvd": {"id": 2149, "name": "Movies DVD", "description": "DVD movies"},
        "movies_hd": {"id": 2150, "name": "Movies HD", "description": "HD movies"},
        "movies_sd": {"id": 2151, "name": "Movies SD", "description": "SD movies"},
        
        # TV Shows
        "tv_4k": {"id": 2152, "name": "TV Shows 4K", "description": "4K TV shows"},
        "tv_bluray": {"id": 2153, "name": "TV Shows Blu-ray", "description": "Blu-ray TV shows"},
        "tv_hd": {"id": 2154, "name": "TV Shows HD", "description": "HD TV shows"},
        "tv_sd": {"id": 2155, "name": "TV Shows SD", "description": "SD TV shows"},
        
        # Music
        "music_flac": {"id": 2156, "name": "Music FLAC", "description": "FLAC music"},
        "music_mp3": {"id": 2157, "name": "Music MP3", "description": "MP3 music"},
        "music_video": {"id": 2158, "name": "Music Videos", "description": "Music videos"},
        
        # Books
        "books_ebooks": {"id": 2159, "name": "E-books", "description": "E-books"},
        "books_audiobooks": {"id": 2160, "name": "Audiobooks", "description": "Audiobooks"},
        
        # Other
        "anime": {"id": 2161, "name": "Anime", "description": "Anime content"},
        "documentaries": {"id": 2162, "name": "Documentaries", "description": "Documentaries"},
    }
    
    return categories


def test_category_rss(session, category_id, category_name, passkey, max_items=5):
    """Test RSS feed for a specific category."""
    print(f"\n📡 Testing category: {category_name} (ID: {category_id})")
    
    rss_url = f"https://www.yggtorrent.top/rss?action=generate&type=subcat&id={category_id}&passkey={passkey}"
    
    try:
        response = session.get(rss_url, timeout=30)
        
        if response.status_code == 200:
            # Parse XML
            root = ET.fromstring(response.text)
            items = root.findall('.//item')
            
            print(f"✅ RSS feed accessible: {len(items)} items found")
            
            # Show first few items
            for i, item in enumerate(items[:max_items]):
                title = item.find('title')
                link = item.find('link')
                
                if title is not None and link is not None:
                    torrent_id = link.text.split('/')[-1].split('-')[0]
                    print(f"  {i+1}. {title.text}")
                    print(f"     ID: {torrent_id}")
            
            if len(items) > max_items:
                print(f"  ... and {len(items) - max_items} more items")
            
            return True, len(items)
        else:
            print(f"❌ RSS feed failed: {response.status_code}")
            return False, 0
            
    except Exception as e:
        print(f"❌ Error testing category {category_name}: {e}")
        return False, 0


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
                            torrent_filename = f"data/category_{category_name}_{safe_title}.torrent"
                            
                            with open(torrent_filename, 'wb') as f:
                                f.write(content)
                            
                            print(f"✅ Downloaded: {torrent_filename}")
                            print(f"📊 File size: {len(content)} bytes")
                            return torrent_filename
                        else:
                            print(f"❌ Downloaded content doesn't look like a torrent file")
                            return None
                    else:
                        print(f"❌ Download failed: {download_response.status_code}")
                        return None
                else:
                    print(f"❌ Could not parse torrent from RSS")
                    return None
            else:
                print(f"❌ No torrents found in category")
                return None
        else:
            print(f"❌ Failed to get RSS feed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error downloading from category {category_name}: {e}")
        return None


def main():
    """Main function."""
    print("🚀 YGG Torrent Category Browser")
    print("=" * 60)
    print("Browse and test different categories using the automated system")
    print("=" * 60)
    
    # Use the working cookie string
    cookie_string = "account_created=true; a3_promo_details=eyJjb3VudGRvd25fZGF0ZSI6IjA5LzMvMjAyNSAyMzo1OTo1OSIsInRzIjoxNzU2OTU4Mzk5fQ==; ygg_=TQoSUGjRCTIJtlhke23R5WT%2CqD6UjPULlwZ%2CV7-THNorSdsU; cf_clearance=pepwzJctlAHMOS5kF3VOcDr89.DzFFYNmDie0xHaCyQ-1756915424-1.2.1.1-pKsLH_R6a1..NHhT0Km1Z5_NNDas3Ta_QuFR9.YiE0jlyS0nmiZrAPsbyXE95xVFn.wl_ObhLMy8wAaKtr_UQ4cr2q85W4jz2V91kZ6kYs0UDjNDWMQ99HSYh2ekZhWviqiGOPVMFivDqqJyP4WmTEQ3nuE2WVV4vx0MnRZHAs17eS6n_jls6FAXiiWOpj0a_zaUaumjHaACUMlerTe_bt_NF_sO7GIKw27gJ7EQr4A"
    
    passkey = "DJdLXYBi2WmyQB0PdNWZ8u9RZEnTqiXT"
    
    print(f"🍪 Using automated cookies ({len(cookie_string.split(';'))} cookies)")
    print(f"🔑 Using passkey: {passkey}")
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    # Get categories
    categories = get_category_info()
    
    print(f"\n📋 Available categories: {len(categories)}")
    
    # Ask user what to do
    print("\nWhat would you like to do?")
    print("1. Test all categories (RSS access)")
    print("2. Test specific categories")
    print("3. Download samples from specific categories")
    print("4. Show all available categories")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    try:
        # Setup session
        session = setup_session_with_cookies(cookie_string)
        
        if choice == "1":
            # Test all categories
            print(f"\n🧪 Testing all {len(categories)} categories...")
            
            results = {}
            for category_key, category_info in categories.items():
                success, item_count = test_category_rss(session, category_info["id"], category_info["name"], passkey)
                results[category_key] = {"success": success, "item_count": item_count}
                time.sleep(1)  # Small delay between requests
            
            # Summary
            print(f"\n{'='*60}")
            print("📊 CATEGORY TEST SUMMARY")
            print(f"{'='*60}")
            
            successful_categories = [k for k, v in results.items() if v["success"]]
            failed_categories = [k for k, v in results.items() if not v["success"]]
            
            print(f"✅ Successful categories: {len(successful_categories)}")
            print(f"❌ Failed categories: {len(failed_categories)}")
            
            if successful_categories:
                print(f"\n✅ Working categories:")
                for cat_key in successful_categories:
                    cat_info = categories[cat_key]
                    item_count = results[cat_key]["item_count"]
                    print(f"  📁 {cat_info['name']} (ID: {cat_info['id']}) - {item_count} items")
            
            if failed_categories:
                print(f"\n❌ Failed categories:")
                for cat_key in failed_categories:
                    cat_info = categories[cat_key]
                    print(f"  📁 {cat_info['name']} (ID: {cat_info['id']})")
            
        elif choice == "2":
            # Test specific categories
            print(f"\nAvailable categories:")
            for i, (cat_key, cat_info) in enumerate(categories.items(), 1):
                print(f"  {i}. {cat_info['name']} (ID: {cat_info['id']}) - {cat_info['description']}")
            
            selection = input(f"\nEnter category numbers (1-{len(categories)}) separated by commas: ").strip()
            
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                selected_categories = [(list(categories.keys())[i], list(categories.values())[i]) for i in indices if 0 <= i < len(categories)]
                
                for cat_key, cat_info in selected_categories:
                    test_category_rss(session, cat_info["id"], cat_info["name"], passkey)
                    time.sleep(1)
                    
            except ValueError:
                print("❌ Invalid selection")
                
        elif choice == "3":
            # Download samples from specific categories
            print(f"\nAvailable categories:")
            for i, (cat_key, cat_info) in enumerate(categories.items(), 1):
                print(f"  {i}. {cat_info['name']} (ID: {cat_info['id']}) - {cat_info['description']}")
            
            selection = input(f"\nEnter category numbers (1-{len(categories)}) separated by commas: ").strip()
            
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                selected_categories = [(list(categories.keys())[i], list(categories.values())[i]) for i in indices if 0 <= i < len(categories)]
                
                downloaded_files = []
                for cat_key, cat_info in selected_categories:
                    torrent_file = download_sample_from_category(session, cat_info["id"], cat_info["name"], passkey)
                    if torrent_file:
                        downloaded_files.append(torrent_file)
                    time.sleep(2)  # Delay between downloads
                
                if downloaded_files:
                    print(f"\n🎉 Downloaded {len(downloaded_files)} sample torrents!")
                    print("📁 Files saved in data/ directory")
                
            except ValueError:
                print("❌ Invalid selection")
                
        elif choice == "4":
            # Show all categories
            print(f"\n📋 All available categories:")
            print(f"{'='*60}")
            
            for cat_key, cat_info in categories.items():
                print(f"📁 {cat_info['name']}")
                print(f"   ID: {cat_info['id']}")
                print(f"   Description: {cat_info['description']}")
                print(f"   RSS URL: https://www.yggtorrent.top/rss?action=generate&type=subcat&id={cat_info['id']}&passkey={passkey}")
                print()
                
        else:
            print("❌ Invalid choice")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n📁 Check the 'data/' directory for results")


if __name__ == "__main__":
    main()

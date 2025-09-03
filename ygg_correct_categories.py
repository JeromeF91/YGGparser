#!/usr/bin/env python3
"""
YGG Torrent Correct Categories Browser
Browse categories using the REAL category mappings discovered through content analysis
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


def get_real_categories():
    """Get the real categories based on content analysis."""
    return {
        # Gaming Categories
        "nintendo_switch": {"id": 2163, "name": "Nintendo Switch Games", "description": "Switch games (NSP, XCI)"},
        "nintendo_switch_2": {"id": 2172, "name": "Nintendo Switch Games 2", "description": "More Switch games"},
        "playstation": {"id": 2164, "name": "PlayStation Games", "description": "PS4/PS5 games"},
        "playstation_2": {"id": 2157, "name": "PlayStation Games 2", "description": "More PlayStation games"},
        "xbox": {"id": 2162, "name": "Xbox Games", "description": "Xbox 360/One/Series games"},
        "retro_nintendo": {"id": 2158, "name": "Retro Nintendo Games", "description": "NES, SNES, N64, GameCube, DS, 3DS, Wii, Wii U"},
        "retro_nintendo_2": {"id": 2148, "name": "Retro Nintendo Games 2", "description": "More retro Nintendo games"},
        "retro_nintendo_3": {"id": 2152, "name": "Retro Nintendo Games 3", "description": "More retro Nintendo games"},
        "retro_nintendo_4": {"id": 2178, "name": "Retro Nintendo Games 4", "description": "More retro Nintendo games"},
        "retro_nintendo_5": {"id": 2179, "name": "Retro Nintendo Games 5", "description": "More retro Nintendo games"},
        "retro_nintendo_6": {"id": 2180, "name": "Retro Nintendo Games 6", "description": "More retro Nintendo games"},
        
        # PC/Software Categories
        "pc_games_1": {"id": 2159, "name": "PC Games/Software 1", "description": "PC games and software"},
        "pc_games_2": {"id": 2160, "name": "PC Games/Software 2", "description": "More PC games and software"},
        "pc_games_3": {"id": 2161, "name": "PC Games/Software 3", "description": "More PC games and software"},
        "pc_games_4": {"id": 2171, "name": "PC Games/Software 4", "description": "More PC games and software"},
        "pc_games_5": {"id": 2173, "name": "PC Games/Software 5", "description": "More PC games and software"},
        "pc_games_6": {"id": 2177, "name": "PC Games/Software 6", "description": "More PC games and software"},
        "software": {"id": 2168, "name": "Software", "description": "General software"},
        "software_2": {"id": 2176, "name": "Software 2", "description": "More software"},
        "software_games": {"id": 2167, "name": "Software/Games", "description": "Mixed software and games"},
        
        # Mobile Categories
        "android_apps": {"id": 2165, "name": "Android Apps", "description": "Android applications"},
        "android_apps_2": {"id": 2166, "name": "Android Apps 2", "description": "More Android apps"},
        "android_apps_3": {"id": 2174, "name": "Android Apps 3", "description": "More Android apps"},
        "android_apps_4": {"id": 2175, "name": "Android Apps 4", "description": "More Android apps"},
        
        # Media Categories
        "music_1": {"id": 2147, "name": "Music 1", "description": "Music files"},
        "music_2": {"id": 2149, "name": "Music 2", "description": "More music"},
        "music_3": {"id": 2151, "name": "Music 3", "description": "More music"},
        "tv_shows": {"id": 2150, "name": "TV Shows", "description": "Television shows"},
        
        # Books/Documents
        "books_1": {"id": 2153, "name": "Books/Documents 1", "description": "Books and documents"},
        "books_2": {"id": 2154, "name": "Books/Documents 2", "description": "More books and documents"},
        "books_3": {"id": 2155, "name": "Books/Documents 3", "description": "More books and documents"},
        "books_4": {"id": 2156, "name": "Books/Documents 4", "description": "More books and documents"},
        
        # Other Categories
        "gps_navigation": {"id": 2169, "name": "GPS/Navigation", "description": "GPS and navigation software"},
        "recent_content": {"id": 2170, "name": "Recent Content", "description": "Recently added content"},
    }


def test_category_rss(session, category_id, category_name, passkey, max_items=3):
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
                            torrent_filename = f"data/correct_{category_name}_{safe_title}.torrent"
                            
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
    print("🚀 YGG Torrent Correct Categories Browser")
    print("=" * 60)
    print("Browse categories using REAL category mappings discovered through content analysis")
    print("=" * 60)
    
    # Use the working cookie string
    cookie_string = "account_created=true; a3_promo_details=eyJjb3VudGRvd25fZGF0ZSI6IjA5LzMvMjAyNSAyMzo1OTo1OSIsInRzIjoxNzU2OTU4Mzk5fQ==; ygg_=TQoSUGjRCTIJtlhke23R5WT%2CqD6UjPULlwZ%2CV7-THNorSdsU; cf_clearance=pepwzJctlAHMOS5kF3VOcDr89.DzFFYNmDie0xHaCyQ-1756915424-1.2.1.1-pKsLH_R6a1..NHhT0Km1Z5_NNDas3Ta_QuFR9.YiE0jlyS0nmiZrAPsbyXE95xVFn.wl_ObhLMy8wAaKtr_UQ4cr2q85W4jz2V91kZ6kYs0UDjNDWMQ99HSYh2ekZhWviqiGOPVMFivDqqJyP4WmTEQ3nuE2WVV4vx0MnRZHAs17eS6n_jls6FAXiiWOpj0a_zaUaumjHaACUMlerTe_bt_NF_sO7GIKw27gJ7EQr4A"
    
    passkey = "DJdLXYBi2WmyQB0PdNWZ8u9RZEnTqiXT"
    
    print(f"🍪 Using automated cookies ({len(cookie_string.split(';'))} cookies)")
    print(f"🔑 Using passkey: {passkey}")
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    # Get real categories
    categories = get_real_categories()
    
    print(f"\n📋 Available REAL categories: {len(categories)}")
    
    # Ask user what to do
    print("\nWhat would you like to do?")
    print("1. Test all categories (RSS access)")
    print("2. Test specific categories")
    print("3. Download samples from specific categories")
    print("4. Show all available categories")
    print("5. Download samples from diverse categories (demo)")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
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
            print(f"\n📋 All available REAL categories:")
            print(f"{'='*60}")
            
            for cat_key, cat_info in categories.items():
                print(f"📁 {cat_info['name']}")
                print(f"   ID: {cat_info['id']}")
                print(f"   Description: {cat_info['description']}")
                print(f"   RSS URL: https://www.yggtorrent.top/rss?action=generate&type=subcat&id={cat_info['id']}&passkey={passkey}")
                print()
                
        elif choice == "5":
            # Download samples from diverse categories (demo)
            print(f"\n🎯 Downloading samples from diverse categories...")
            
            # Select diverse categories
            demo_categories = [
                ("nintendo_switch", "Nintendo Switch Games"),
                ("playstation", "PlayStation Games"),
                ("xbox", "Xbox Games"),
                ("pc_games_1", "PC Games/Software"),
                ("music_1", "Music"),
                ("books_1", "Books/Documents"),
                ("android_apps", "Android Apps"),
            ]
            
            downloaded_files = []
            for cat_key, cat_name in demo_categories:
                if cat_key in categories:
                    cat_info = categories[cat_key]
                    torrent_file = download_sample_from_category(session, cat_info["id"], cat_name, passkey)
                    if torrent_file:
                        downloaded_files.append(torrent_file)
                    time.sleep(2)
            
            if downloaded_files:
                print(f"\n🎉 Downloaded {len(downloaded_files)} diverse samples!")
                print("📁 Files saved in data/ directory")
                
        else:
            print("❌ Invalid choice")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n📁 Check the 'data/' directory for results")


if __name__ == "__main__":
    main()

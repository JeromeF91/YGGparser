#!/usr/bin/env python3
"""
YGG Torrent Final Category Browser
Browse categories using the REAL category names extracted from RSS feeds
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
    """Get the real categories from the extracted data."""
    try:
        with open('data/extracted_categories_simple.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Extracted categories file not found. Please run ygg_extract_category_names.py first.")
        return {}


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
                category = item.find('category')
                
                if title is not None and link is not None:
                    torrent_id = link.text.split('/')[-1].split('-')[0]
                    category_name_from_item = category.text if category is not None else "Unknown"
                    print(f"  {i+1}. {title.text}")
                    print(f"     ID: {torrent_id} | Category: {category_name_from_item}")
            
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
                category = first_item.find('category')
                
                if title is not None and link is not None:
                    torrent_id = link.text.split('/')[-1].split('-')[0]
                    torrent_title = title.text
                    category_name_from_item = category.text if category is not None else "Unknown"
                    
                    print(f"  📋 Torrent: {torrent_title}")
                    print(f"  🆔 ID: {torrent_id} | Category: {category_name_from_item}")
                    
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
                            torrent_filename = f"data/final_{category_name}_{safe_title}.torrent"
                            
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
    print("🚀 YGG Torrent Final Category Browser")
    print("=" * 60)
    print("Browse categories using REAL category names extracted from RSS feeds")
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
    
    if not categories:
        return
    
    print(f"\n📋 Available REAL categories: {len(categories)}")
    
    # Ask user what to do
    print("\nWhat would you like to do?")
    print("1. Test all categories (RSS access)")
    print("2. Test specific categories")
    print("3. Download samples from specific categories")
    print("4. Show all available categories")
    print("5. Download samples from diverse categories (demo)")
    print("6. Browse by category type")
    
    choice = input("\nEnter your choice (1-6): ").strip()
    
    try:
        # Setup session
        session = setup_session_with_cookies(cookie_string)
        
        if choice == "1":
            # Test all categories
            print(f"\n🧪 Testing all {len(categories)} categories...")
            
            results = {}
            for category_id, category_info in categories.items():
                success, item_count = test_category_rss(session, category_info["id"], category_info["name"], passkey)
                results[category_id] = {"success": success, "item_count": item_count}
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
                for cat_id in successful_categories:
                    cat_info = categories[cat_id]
                    item_count = results[cat_id]["item_count"]
                    print(f"  📁 {cat_info['name']} (ID: {cat_info['id']}) - {item_count} items")
            
            if failed_categories:
                print(f"\n❌ Failed categories:")
                for cat_id in failed_categories:
                    cat_info = categories[cat_id]
                    print(f"  📁 {cat_info['name']} (ID: {cat_info['id']})")
            
        elif choice == "2":
            # Test specific categories
            print(f"\nAvailable categories:")
            for i, (cat_id, cat_info) in enumerate(categories.items(), 1):
                print(f"  {i}. {cat_info['name']} (ID: {cat_info['id']}) - {cat_info['item_count']} items")
            
            selection = input(f"\nEnter category numbers (1-{len(categories)}) separated by commas: ").strip()
            
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                selected_categories = [(list(categories.keys())[i], list(categories.values())[i]) for i in indices if 0 <= i < len(categories)]
                
                for cat_id, cat_info in selected_categories:
                    test_category_rss(session, cat_info["id"], cat_info["name"], passkey)
                    time.sleep(1)
                    
            except ValueError:
                print("❌ Invalid selection")
                
        elif choice == "3":
            # Download samples from specific categories
            print(f"\nAvailable categories:")
            for i, (cat_id, cat_info) in enumerate(categories.items(), 1):
                print(f"  {i}. {cat_info['name']} (ID: {cat_info['id']}) - {cat_info['item_count']} items")
            
            selection = input(f"\nEnter category numbers (1-{len(categories)}) separated by commas: ").strip()
            
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                selected_categories = [(list(categories.keys())[i], list(categories.values())[i]) for i in indices if 0 <= i < len(categories)]
                
                downloaded_files = []
                for cat_id, cat_info in selected_categories:
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
            
            for cat_id, cat_info in categories.items():
                print(f"📁 {cat_info['name']}")
                print(f"   ID: {cat_info['id']}")
                print(f"   Items: {cat_info['item_count']}")
                print(f"   Parent: {cat_info['parent_name']}")
                print(f"   RSS URL: https://www.yggtorrent.top/rss?action=generate&type=subcat&id={cat_info['id']}&passkey={passkey}")
                print()
                
        elif choice == "5":
            # Download samples from diverse categories (demo)
            print(f"\n🎯 Downloading samples from diverse categories...")
            
            # Select diverse categories
            demo_categories = [
                ("2163", "Nintendo"),
                ("2164", "Sony"),
                ("2162", "Microsoft"),
                ("2171", "Linux"),
                ("2148", "Musique"),
                ("2154", "Livres"),
                ("2183", "Film"),
            ]
            
            downloaded_files = []
            for cat_id, cat_name in demo_categories:
                if cat_id in categories:
                    cat_info = categories[cat_id]
                    torrent_file = download_sample_from_category(session, cat_info["id"], cat_name, passkey)
                    if torrent_file:
                        downloaded_files.append(torrent_file)
                    time.sleep(2)
            
            if downloaded_files:
                print(f"\n🎉 Downloaded {len(downloaded_files)} diverse samples!")
                print("📁 Files saved in data/ directory")
                
        elif choice == "6":
            # Browse by category type
            print(f"\n📋 Browse by category type:")
            
            # Group categories by type
            category_groups = {
                "Gaming": ["Nintendo", "Sony", "Microsoft", "Jeux"],
                "Operating Systems": ["Linux", "MacOS", "Windows"],
                "Mobile": ["Smartphone", "Tablette"],
                "Audio/Music": ["Musique", "Audio", "Karaoké", "Samples", "Podcast Radio"],
                "Books/Documents": ["Livres", "Ebooks", "Mangas", "Bds", "Comics", "Presse"],
                "Video/Media": ["Film", "Films", "Série TV", "Animation", "Documentaire", "Sport"],
                "Other": ["Autre", "Divers", "Formation", "Applications"]
            }
            
            for group_name, group_categories in category_groups.items():
                print(f"\n📁 {group_name}:")
                for cat_name in group_categories:
                    # Find categories with this name
                    matching_cats = [cat for cat in categories.values() if cat['name'] == cat_name]
                    for cat in matching_cats:
                        print(f"  📄 {cat['name']} (ID: {cat['id']}) - {cat['item_count']} items")
                
        else:
            print("❌ Invalid choice")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n📁 Check the 'data/' directory for results")


if __name__ == "__main__":
    main()

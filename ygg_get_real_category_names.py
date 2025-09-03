#!/usr/bin/env python3
"""
YGG Torrent Real Category Names
Get the actual category names by examining the parent category pages
"""

import os
import json
import time
import requests
import cloudscraper
from bs4 import BeautifulSoup


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


def get_real_category_names(session, parent_id, passkey):
    """Get real category names by examining the parent category page."""
    print(f"  🔍 Getting real names for parent category {parent_id}...")
    
    try:
        # Get the parent category page
        parent_url = f"https://www.yggtorrent.top/rss?parent_category={parent_id}"
        response = session.get(parent_url, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for the actual category names in the page
            # They might be in different formats - let's try multiple approaches
            
            category_names = {}
            
            # Method 1: Look for links with subcategory IDs
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # Look for subcategory links
                if 'type=subcat&id=' in href:
                    subcat_id = href.split('type=subcat&id=')[1].split('&')[0].split('#')[0]
                    
                    if subcat_id.isdigit() and text and text != "Accéder au flux RSS":
                        category_names[subcat_id] = text
            
            # Method 2: Look for table rows or list items that might contain category names
            # Try to find patterns in the HTML structure
            
            # Method 3: Look for any text that might be category names
            # This is a fallback method
            
            if not category_names:
                # If we can't find specific names, let's try to get them from the page structure
                # Look for any text that might indicate category names
                page_text = soup.get_text()
                
                # Try to find patterns that might indicate category names
                # This is a heuristic approach
                pass
            
            print(f"    ✅ Found {len(category_names)} real category names")
            return category_names
            
        else:
            print(f"    ❌ Failed to access parent category: {response.status_code}")
            return {}
            
    except Exception as e:
        print(f"    ❌ Error getting real category names: {e}")
        return {}


def analyze_category_content(session, category_id, passkey):
    """Analyze the content of a category to determine its type."""
    print(f"    Analyzing category {category_id}...", end=" ")
    
    rss_url = f"https://www.yggtorrent.top/rss?action=generate&type=subcat&id={category_id}&passkey={passkey}"
    
    try:
        response = session.get(rss_url, timeout=30)
        
        if response.status_code == 200:
            # Parse XML and analyze content
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.text)
            items = root.findall('.//item')
            
            if len(items) > 0:
                # Analyze the first few items to determine category type
                titles = []
                for item in items[:3]:
                    title = item.find('title')
                    if title is not None:
                        titles.append(title.text)
                
                # Analyze titles to determine category
                category_type = analyze_titles(titles)
                
                print(f"✅ {len(items)} items - {category_type}")
                return {
                    'id': category_id,
                    'name': category_type,
                    'item_count': len(items),
                    'sample_titles': titles[:2]
                }
            else:
                print("❌ No items")
                return None
        else:
            print(f"❌ {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def analyze_titles(titles):
    """Analyze titles to determine the category type."""
    if not titles:
        return "Unknown"
    
    # Convert all titles to lowercase for analysis
    all_text = " ".join(titles).lower()
    
    # Gaming categories
    if any(keyword in all_text for keyword in ['switch', 'nsp', 'xci', 'mig switch']):
        return "Nintendo Switch Games"
    elif any(keyword in all_text for keyword in ['ps4', 'ps5', 'playstation', 'cusa']):
        return "PlayStation Games"
    elif any(keyword in all_text for keyword in ['xbox', 'x360', 'xbox360']):
        return "Xbox Games"
    elif any(keyword in all_text for keyword in ['pc', 'windows', 'win x64', 'linux', 'mac']):
        return "PC Games/Software"
    elif any(keyword in all_text for keyword in ['android', 'apk', 'mobile']):
        return "Android Apps"
    elif any(keyword in all_text for keyword in ['3ds', 'cia']):
        return "Nintendo 3DS Games"
    elif any(keyword in all_text for keyword in ['wii', 'wii u']):
        return "Nintendo Wii/Wii U Games"
    elif any(keyword in all_text for keyword in ['psp', 'vita']):
        return "PlayStation Portable/Vita Games"
    elif any(keyword in all_text for keyword in ['nes', 'snes', 'n64', 'gamecube', 'ds']):
        return "Retro Nintendo Games"
    
    # Media categories
    elif any(keyword in all_text for keyword in ['blu-ray', 'bluray', 'bdrip', 'webrip', 'hdtv', 'dvdrip']):
        return "Movies"
    elif any(keyword in all_text for keyword in ['saison', 'season', 'episode', 'serie', 'series']):
        return "TV Shows"
    elif any(keyword in all_text for keyword in ['flac', 'mp3', '320', '192', 'album', 'cd']):
        return "Music"
    elif any(keyword in all_text for keyword in ['anime', 'manga', 'japanese']):
        return "Anime/Manga"
    
    # Books and documents
    elif any(keyword in all_text for keyword in ['pdf', 'epub', 'ebook', 'livre', 'book']):
        return "Books/Documents"
    elif any(keyword in all_text for keyword in ['audiobook', 'audio book']):
        return "Audiobooks"
    
    # Software and applications
    elif any(keyword in all_text for keyword in ['software', 'application', 'app', 'program']):
        return "Software"
    elif any(keyword in all_text for keyword in ['gps', 'navigation', 'map']):
        return "GPS/Navigation"
    
    # Other
    elif any(keyword in all_text for keyword in ['emulation', 'rom', 'mame', 'retro']):
        return "Emulation/ROMs"
    elif any(keyword in all_text for keyword in ['xxx', 'adult']):
        return "Adult Content"
    elif any(keyword in all_text for keyword in ['3d', 'imprimante', 'stl']):
        return "3D Printing"
    elif any(keyword in all_text for keyword in ['nulled', 'crack', 'precrack']):
        return "Cracked Software"
    
    # If we can't determine, look at common patterns
    elif any(keyword in all_text for keyword in ['[', ']', 'v1.', 'v2.', 'build']):
        return "Software/Games"
    elif any(keyword in all_text for keyword in ['2024', '2025', '2023']):
        return "Recent Content"
    else:
        return "Mixed/Unknown Content"


def main():
    """Main function."""
    print("🚀 YGG Torrent Real Category Names")
    print("=" * 60)
    print("Getting real category names and analyzing content")
    print("=" * 60)
    
    # Use the working cookie string
    cookie_string = "account_created=true; a3_promo_details=eyJjb3VudGRvd25fZGF0ZSI6IjA5LzMvMjAyNSAyMzo1OTo1OSIsInRzIjoxNzU2OTU4Mzk5fQ==; ygg_=TQoSUGjRCTIJtlhke23R5WT%2CqD6UjPULlwZ%2CV7-THNorSdsU; cf_clearance=pepwzJctlAHMOS5kF3VOcDr89.DzFFYNmDie0xHaCyQ-1756915424-1.2.1.1-pKsLH_R6a1..NHhT0Km1Z5_NNDas3Ta_QuFR9.YiE0jlyS0nmiZrAPsbyXE95xVFn.wl_ObhLMy8wAaKtr_UQ4cr2q85W4jz2V91kZ6kYs0UDjNDWMQ99HSYh2ekZhWviqiGOPVMFivDqqJyP4WmTEQ3nuE2WVV4vx0MnRZHAs17eS6n_jls6FAXiiWOpj0a_zaUaumjHaACUMlerTe_bt_NF_sO7GIKw27gJ7EQr4A"
    
    passkey = "DJdLXYBi2WmyQB0PdNWZ8u9RZEnTqiXT"
    
    print(f"🍪 Using automated cookies ({len(cookie_string.split(';'))} cookies)")
    print(f"🔑 Using passkey: {passkey}")
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    # Load the discovered RSS structure
    try:
        with open('data/rss_structure_discovery.json', 'r') as f:
            rss_data = json.load(f)
        
        organized_categories = rss_data['organized_categories']
        print(f"📊 Loaded RSS structure with {len(organized_categories)} parent categories")
        
    except FileNotFoundError:
        print("❌ RSS structure file not found. Please run ygg_discover_rss_structure.py first.")
        return
    
    try:
        # Setup session
        session = setup_session_with_cookies(cookie_string)
        
        # Analyze categories to get real names
        print(f"\n{'='*60}")
        print("ANALYZING CATEGORIES FOR REAL NAMES")
        print(f"{'='*60}")
        
        all_categories_with_names = {}
        
        for parent_id, parent_data in organized_categories.items():
            parent_info = parent_data['parent_info']
            subcategories = parent_data['subcategories']
            
            print(f"\n📁 Analyzing parent category: {parent_info['name']} (ID: {parent_id})")
            
            # Get real category names from the parent page
            real_names = get_real_category_names(session, parent_id, passkey)
            
            # Analyze each subcategory
            for subcat_id, subcat_info in subcategories.items():
                # Try to get real name first
                real_name = real_names.get(subcat_id, subcat_info['name'])
                
                # Analyze content to determine category type
                analysis = analyze_category_content(session, subcat_id, passkey)
                
                if analysis:
                    all_categories_with_names[subcat_id] = {
                        'id': int(subcat_id),
                        'name': analysis['name'],
                        'real_name': real_name,
                        'parent_id': parent_id,
                        'parent_name': parent_info['name'],
                        'item_count': analysis['item_count'],
                        'sample_titles': analysis['sample_titles'],
                        'rss_url': f"https://www.yggtorrent.top/rss?action=generate&type=subcat&id={subcat_id}&passkey={passkey}"
                    }
                
                time.sleep(0.5)  # Small delay between requests
            
            time.sleep(1)  # Delay between parent categories
        
        # Summary
        print(f"\n{'='*60}")
        print("📊 REAL CATEGORY NAMES SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Categories analyzed: {len(all_categories_with_names)}")
        
        if all_categories_with_names:
            # Group by category type
            category_groups = {}
            for cat_id, cat_info in all_categories_with_names.items():
                cat_type = cat_info['name']
                if cat_type not in category_groups:
                    category_groups[cat_type] = []
                category_groups[cat_type].append(cat_info)
            
            print(f"\n📋 Categories grouped by type:")
            for cat_type, categories in category_groups.items():
                print(f"  📁 {cat_type}: {len(categories)} categories")
                for cat in categories[:3]:  # Show first 3
                    print(f"     ID {cat['id']}: {cat['real_name']} ({cat['item_count']} items)")
                if len(categories) > 3:
                    print(f"     ... and {len(categories) - 3} more")
            
            # Save results
            results = {
                "analyzed_at": time.strftime('%Y-%m-%d %H:%M:%S'),
                "total_categories": len(all_categories_with_names),
                "categories": all_categories_with_names,
                "category_groups": category_groups
            }
            
            results_file = "data/real_category_names.json"
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"\n💾 Real category names saved to: {results_file}")
            
            # Create a simple category list for easy use
            simple_categories = {}
            for cat_id, cat_info in all_categories_with_names.items():
                simple_categories[cat_id] = {
                    "id": cat_info["id"],
                    "name": cat_info["name"],
                    "real_name": cat_info["real_name"],
                    "parent_id": cat_info["parent_id"],
                    "parent_name": cat_info["parent_name"],
                    "item_count": cat_info["item_count"],
                    "rss_url": cat_info["rss_url"]
                }
            
            simple_file = "data/real_categories_simple.json"
            with open(simple_file, 'w') as f:
                json.dump(simple_categories, f, indent=2)
            
            print(f"💾 Simple real categories saved to: {simple_file}")
            
        else:
            print("❌ No categories analyzed")
            
    except Exception as e:
        print(f"❌ Error during category name analysis: {e}")
    
    print("\n📁 Check the 'data/' directory for results")


if __name__ == "__main__":
    main()

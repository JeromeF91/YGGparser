#!/usr/bin/env python3
"""
YGG Torrent Category Analysis
Analyze the actual content of RSS feeds to determine real category names
"""

import os
import json
import time
import requests
import cloudscraper
import xml.etree.ElementTree as ET
from collections import Counter


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


def analyze_rss_content(session, category_id, passkey, max_items=5):
    """Analyze the content of an RSS feed to determine the category type."""
    print(f"  Analyzing category {category_id}...", end=" ")
    
    rss_url = f"https://www.yggtorrent.top/rss?action=generate&type=subcat&id={category_id}&passkey={passkey}"
    
    try:
        response = session.get(rss_url, timeout=30)
        
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            items = root.findall('.//item')
            
            if len(items) > 0:
                # Analyze the first few items to determine category type
                titles = []
                for item in items[:max_items]:
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
                    'sample_titles': titles[:3],
                    'rss_url': rss_url
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
    print("🚀 YGG Torrent Category Analysis")
    print("=" * 60)
    print("Analyzing RSS feed content to determine real category names")
    print("=" * 60)
    
    # Use the working cookie string
    cookie_string = "account_created=true; a3_promo_details=eyJjb3VudGRvd25fZGF0ZSI6IjA5LzMvMjAyNSAyMzo1OTo1OSIsInRzIjoxNzU2OTU4Mzk5fQ==; ygg_=TQoSUGjRCTIJtlhke23R5WT%2CqD6UjPULlwZ%2CV7-THNorSdsU; cf_clearance=pepwzJctlAHMOS5kF3VOcDr89.DzFFYNmDie0xHaCyQ-1756915424-1.2.1.1-pKsLH_R6a1..NHhT0Km1Z5_NNDas3Ta_QuFR9.YiE0jlyS0nmiZrAPsbyXE95xVFn.wl_ObhLMy8wAaKtr_UQ4cr2q85W4jz2V91kZ6kYs0UDjNDWMQ99HSYh2ekZhWviqiGOPVMFivDqqJyP4WmTEQ3nuE2WVV4vx0MnRZHAs17eS6n_jls6FAXiiWOpj0a_zaUaumjHaACUMlerTe_bt_NF_sO7GIKw27gJ7EQr4A"
    
    passkey = "DJdLXYBi2WmyQB0PdNWZ8u9RZEnTqiXT"
    
    print(f"🍪 Using automated cookies ({len(cookie_string.split(';'))} cookies)")
    print(f"🔑 Using passkey: {passkey}")
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    # Test the working category IDs we found
    working_categories = list(range(2147, 2181))  # 2147-2180 based on our discovery
    
    try:
        # Setup session
        session = setup_session_with_cookies(cookie_string)
        
        analyzed_categories = {}
        
        print(f"\n🧪 Analyzing {len(working_categories)} working categories...")
        
        for category_id in working_categories:
            result = analyze_rss_content(session, category_id, passkey)
            if result:
                analyzed_categories[category_id] = result
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.5)
        
        # Summary
        print(f"\n{'='*60}")
        print("📊 CATEGORY ANALYSIS SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Categories analyzed: {len(analyzed_categories)}")
        
        if analyzed_categories:
            print(f"\n📋 Analyzed categories:")
            for cat_id, cat_info in sorted(analyzed_categories.items()):
                print(f"  📁 ID {cat_id}: {cat_info['name']} ({cat_info['item_count']} items)")
                if cat_info['sample_titles']:
                    print(f"      Sample: {cat_info['sample_titles'][0][:60]}...")
            
            # Group by category type
            category_groups = {}
            for cat_id, cat_info in analyzed_categories.items():
                cat_type = cat_info['name']
                if cat_type not in category_groups:
                    category_groups[cat_type] = []
                category_groups[cat_type].append(cat_id)
            
            print(f"\n📊 Categories grouped by type:")
            for cat_type, cat_ids in category_groups.items():
                print(f"  📁 {cat_type}: {len(cat_ids)} categories - IDs {min(cat_ids)}-{max(cat_ids)}")
            
            # Save analyzed categories
            analysis_results = {
                "analyzed_at": time.strftime('%Y-%m-%d %H:%M:%S'),
                "total_categories": len(analyzed_categories),
                "categories": analyzed_categories,
                "category_groups": category_groups
            }
            
            results_file = "data/analyzed_categories.json"
            with open(results_file, 'w') as f:
                json.dump(analysis_results, f, indent=2)
            
            print(f"\n💾 Analyzed categories saved to: {results_file}")
            
            # Create a clean category list
            clean_categories = {}
            for cat_id, cat_info in analyzed_categories.items():
                clean_categories[cat_id] = {
                    "id": cat_info["id"],
                    "name": cat_info["name"],
                    "item_count": cat_info["item_count"],
                    "rss_url": f"https://www.yggtorrent.top/rss?action=generate&type=subcat&id={cat_id}&passkey={passkey}"
                }
            
            clean_file = "data/categories_clean.json"
            with open(clean_file, 'w') as f:
                json.dump(clean_categories, f, indent=2)
            
            print(f"💾 Clean category list saved to: {clean_file}")
            
        else:
            print("❌ No categories analyzed")
            
    except Exception as e:
        print(f"❌ Error during category analysis: {e}")
    
    print("\n📁 Check the 'data/' directory for results")


if __name__ == "__main__":
    main()

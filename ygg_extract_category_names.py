#!/usr/bin/env python3
"""
YGG Torrent Extract Category Names from RSS
Extract real category names from the <category> tags in RSS feed items
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


def extract_category_names_from_rss(session, category_id, passkey, max_items=10):
    """Extract category names from RSS feed items."""
    print(f"  Extracting category names from RSS {category_id}...", end=" ")
    
    rss_url = f"https://www.yggtorrent.top/rss?action=generate&type=subcat&id={category_id}&passkey={passkey}"
    
    try:
        response = session.get(rss_url, timeout=30)
        
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            items = root.findall('.//item')
            
            if len(items) > 0:
                # Extract category names from items
                category_names = []
                for item in items[:max_items]:
                    category_elem = item.find('category')
                    if category_elem is not None and category_elem.text:
                        category_names.append(category_elem.text.strip())
                
                # Get the most common category name
                if category_names:
                    category_counter = Counter(category_names)
                    most_common_category = category_counter.most_common(1)[0][0]
                    print(f"✅ {len(items)} items - Category: '{most_common_category}'")
                    
                    return {
                        'id': category_id,
                        'name': most_common_category,
                        'item_count': len(items),
                        'all_categories': list(category_counter.keys()),
                        'category_counts': dict(category_counter)
                    }
                else:
                    print(f"❌ No category tags found")
                    return None
            else:
                print(f"❌ No items")
                return None
        else:
            print(f"❌ {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    """Main function."""
    print("🚀 YGG Torrent Extract Category Names from RSS")
    print("=" * 60)
    print("Extracting real category names from <category> tags in RSS feed items")
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
        
        # Extract category names from RSS feeds
        print(f"\n{'='*60}")
        print("EXTRACTING CATEGORY NAMES FROM RSS FEEDS")
        print(f"{'='*60}")
        
        all_categories_with_real_names = {}
        
        for parent_id, parent_data in organized_categories.items():
            parent_info = parent_data['parent_info']
            subcategories = parent_data['subcategories']
            
            print(f"\n📁 Processing parent category: {parent_info['name']} (ID: {parent_id})")
            
            for subcat_id, subcat_info in subcategories.items():
                # Extract real category name from RSS
                category_data = extract_category_names_from_rss(session, subcat_id, passkey)
                
                if category_data:
                    all_categories_with_real_names[subcat_id] = {
                        'id': category_data['id'],
                        'name': category_data['name'],
                        'parent_id': parent_id,
                        'parent_name': parent_info['name'],
                        'item_count': category_data['item_count'],
                        'all_categories': category_data['all_categories'],
                        'category_counts': category_data['category_counts'],
                        'rss_url': f"https://www.yggtorrent.top/rss?action=generate&type=subcat&id={subcat_id}&passkey={passkey}"
                    }
                
                time.sleep(0.5)  # Small delay between requests
            
            time.sleep(1)  # Delay between parent categories
        
        # Summary
        print(f"\n{'='*60}")
        print("📊 REAL CATEGORY NAMES EXTRACTION SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Categories processed: {len(all_categories_with_real_names)}")
        
        if all_categories_with_real_names:
            # Group by category name
            category_groups = {}
            for cat_id, cat_info in all_categories_with_real_names.items():
                cat_name = cat_info['name']
                if cat_name not in category_groups:
                    category_groups[cat_name] = []
                category_groups[cat_name].append(cat_info)
            
            print(f"\n📋 Categories grouped by name:")
            for cat_name, categories in sorted(category_groups.items()):
                print(f"  📁 {cat_name}: {len(categories)} subcategories")
                for cat in categories:
                    print(f"     ID {cat['id']}: {cat['item_count']} items")
                    if len(cat['all_categories']) > 1:
                        print(f"       Other categories found: {', '.join(cat['all_categories'][:3])}")
            
            # Save results
            results = {
                "extracted_at": time.strftime('%Y-%m-%d %H:%M:%S'),
                "total_categories": len(all_categories_with_real_names),
                "categories": all_categories_with_real_names,
                "category_groups": category_groups
            }
            
            results_file = "data/extracted_category_names.json"
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"\n💾 Extracted category names saved to: {results_file}")
            
            # Create a simple category list for easy use
            simple_categories = {}
            for cat_id, cat_info in all_categories_with_real_names.items():
                simple_categories[cat_id] = {
                    "id": cat_info["id"],
                    "name": cat_info["name"],
                    "parent_id": cat_info["parent_id"],
                    "parent_name": cat_info["parent_name"],
                    "item_count": cat_info["item_count"],
                    "rss_url": cat_info["rss_url"]
                }
            
            simple_file = "data/extracted_categories_simple.json"
            with open(simple_file, 'w') as f:
                json.dump(simple_categories, f, indent=2)
            
            print(f"💾 Simple extracted categories saved to: {simple_file}")
            
            # Show some examples
            print(f"\n📋 Example categories found:")
            for cat_name, categories in list(category_groups.items())[:10]:
                example_cat = categories[0]
                print(f"  📁 {cat_name} (ID: {example_cat['id']}) - {example_cat['item_count']} items")
            
        else:
            print("❌ No categories processed")
            
    except Exception as e:
        print(f"❌ Error during category name extraction: {e}")
    
    print("\n📁 Check the 'data/' directory for results")


if __name__ == "__main__":
    main()

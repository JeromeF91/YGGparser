#!/usr/bin/env python3
"""
YGG Torrent RSS Structure Discovery
Discover the real category hierarchy by browsing the RSS page structure
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


def discover_rss_page_structure(session):
    """Discover the RSS page structure and parent categories."""
    print("🔍 Discovering RSS page structure...")
    
    try:
        # Get the main RSS page
        rss_url = "https://www.yggtorrent.top/rss"
        response = session.get(rss_url, timeout=30)
        
        if response.status_code == 200:
            print("✅ Successfully accessed RSS page")
            
            # Parse HTML to find category links
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for links with parent_category parameter
            parent_categories = {}
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # Look for parent_category links
                if 'parent_category=' in href:
                    # Extract parent category ID
                    parent_id = href.split('parent_category=')[1].split('&')[0].split('#')[0]
                    
                    if parent_id.isdigit() and text:
                        parent_categories[parent_id] = {
                            'id': int(parent_id),
                            'name': text,
                            'url': href
                        }
            
            print(f"📊 Found {len(parent_categories)} parent categories from RSS page")
            return parent_categories
            
        else:
            print(f"❌ Failed to access RSS page: {response.status_code}")
            return {}
            
    except Exception as e:
        print(f"❌ Error discovering RSS page structure: {e}")
        return {}


def discover_subcategories(session, parent_id, parent_name, passkey):
    """Discover subcategories for a parent category."""
    print(f"  🔍 Discovering subcategories for {parent_name} (ID: {parent_id})...")
    
    try:
        # Get the parent category RSS page
        parent_url = f"https://www.yggtorrent.top/rss?parent_category={parent_id}"
        response = session.get(parent_url, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            subcategories = {}
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # Look for subcategory links (type=subcat)
                if 'type=subcat&id=' in href:
                    # Extract subcategory ID
                    subcat_id = href.split('type=subcat&id=')[1].split('&')[0].split('#')[0]
                    
                    if subcat_id.isdigit() and text:
                        subcategories[subcat_id] = {
                            'id': int(subcat_id),
                            'name': text,
                            'url': href,
                            'parent_id': parent_id,
                            'parent_name': parent_name
                        }
            
            print(f"    ✅ Found {len(subcategories)} subcategories")
            return subcategories
            
        else:
            print(f"    ❌ Failed to access parent category: {response.status_code}")
            return {}
            
    except Exception as e:
        print(f"    ❌ Error discovering subcategories: {e}")
        return {}


def test_rss_feed(session, category_id, category_name, passkey):
    """Test if an RSS feed is accessible and has content."""
    rss_url = f"https://www.yggtorrent.top/rss?action=generate&type=subcat&id={category_id}&passkey={passkey}"
    
    try:
        response = session.get(rss_url, timeout=30)
        
        if response.status_code == 200:
            # Check if it's valid XML with items
            try:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.text)
                items = root.findall('.//item')
                
                if len(items) > 0:
                    return True, len(items)
                else:
                    return False, 0
            except:
                return False, 0
        else:
            return False, 0
            
    except Exception as e:
        return False, 0


def main():
    """Main function."""
    print("🚀 YGG Torrent RSS Structure Discovery")
    print("=" * 60)
    print("Discovering real category hierarchy from RSS page structure")
    print("=" * 60)
    
    # Use the working cookie string
    cookie_string = "account_created=true; a3_promo_details=eyJjb3VudGRvd25fZGF0ZSI6IjA5LzMvMjAyNSAyMzo1OTo1OSIsInRzIjoxNzU2OTU4Mzk5fQ==; ygg_=TQoSUGjRCTIJtlhke23R5WT%2CqD6UjPULlwZ%2CV7-THNorSdsU; cf_clearance=pepwzJctlAHMOS5kF3VOcDr89.DzFFYNmDie0xHaCyQ-1756915424-1.2.1.1-pKsLH_R6a1..NHhT0Km1Z5_NNDas3Ta_QuFR9.YiE0jlyS0nmiZrAPsbyXE95xVFn.wl_ObhLMy8wAaKtr_UQ4cr2q85W4jz2V91kZ6kYs0UDjNDWMQ99HSYh2ekZhWviqiGOPVMFivDqqJyP4WmTEQ3nuE2WVV4vx0MnRZHAs17eS6n_jls6FAXiiWOpj0a_zaUaumjHaACUMlerTe_bt_NF_sO7GIKw27gJ7EQr4A"
    
    passkey = "DJdLXYBi2WmyQB0PdNWZ8u9RZEnTqiXT"
    
    print(f"🍪 Using automated cookies ({len(cookie_string.split(';'))} cookies)")
    print(f"🔑 Using passkey: {passkey}")
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    try:
        # Setup session
        session = setup_session_with_cookies(cookie_string)
        
        # Step 1: Discover parent categories from RSS page
        print(f"\n{'='*60}")
        print("STEP 1: Discovering Parent Categories")
        print(f"{'='*60}")
        parent_categories = discover_rss_page_structure(session)
        
        if not parent_categories:
            print("❌ No parent categories found")
            return
        
        print(f"\n📋 Found parent categories:")
        for parent_id, parent_info in sorted(parent_categories.items(), key=lambda x: int(x[0])):
            print(f"  📁 ID {parent_id}: {parent_info['name']}")
        
        # Step 2: Discover subcategories for each parent
        print(f"\n{'='*60}")
        print("STEP 2: Discovering Subcategories")
        print(f"{'='*60}")
        
        all_subcategories = {}
        for parent_id, parent_info in parent_categories.items():
            subcategories = discover_subcategories(session, parent_id, parent_info['name'], passkey)
            all_subcategories.update(subcategories)
            time.sleep(1)  # Small delay between requests
        
        print(f"\n📊 Total subcategories discovered: {len(all_subcategories)}")
        
        # Step 3: Test RSS feeds for subcategories
        print(f"\n{'='*60}")
        print("STEP 3: Testing RSS Feeds")
        print(f"{'='*60}")
        
        working_subcategories = {}
        for subcat_id, subcat_info in all_subcategories.items():
            print(f"  Testing subcategory {subcat_id}: {subcat_info['name']}...", end=" ")
            success, item_count = test_rss_feed(session, subcat_id, subcat_info['name'], passkey)
            
            if success:
                subcat_info['item_count'] = item_count
                subcat_info['rss_working'] = True
                working_subcategories[subcat_id] = subcat_info
                print(f"✅ {item_count} items")
            else:
                print("❌ No items")
            
            time.sleep(0.5)  # Small delay between requests
        
        # Step 4: Organize results by parent category
        print(f"\n{'='*60}")
        print("STEP 4: Organizing Results")
        print(f"{'='*60}")
        
        organized_categories = {}
        for parent_id, parent_info in parent_categories.items():
            parent_subcategories = {}
            for subcat_id, subcat_info in working_subcategories.items():
                if subcat_info['parent_id'] == parent_id:
                    parent_subcategories[subcat_id] = subcat_info
            
            if parent_subcategories:
                organized_categories[parent_id] = {
                    'parent_info': parent_info,
                    'subcategories': parent_subcategories,
                    'subcategory_count': len(parent_subcategories)
                }
        
        # Summary
        print(f"\n{'='*60}")
        print("📊 RSS STRUCTURE DISCOVERY SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Parent categories found: {len(parent_categories)}")
        print(f"✅ Total subcategories found: {len(all_subcategories)}")
        print(f"✅ Working subcategories: {len(working_subcategories)}")
        print(f"✅ Organized parent categories: {len(organized_categories)}")
        
        if organized_categories:
            print(f"\n📋 Category hierarchy:")
            for parent_id, parent_data in sorted(organized_categories.items(), key=lambda x: int(x[0])):
                parent_info = parent_data['parent_info']
                subcategories = parent_data['subcategories']
                
                print(f"\n📁 {parent_info['name']} (ID: {parent_id})")
                print(f"   Subcategories: {len(subcategories)}")
                
                for subcat_id, subcat_info in sorted(subcategories.items(), key=lambda x: int(x[0])):
                    item_count = subcat_info.get('item_count', 0)
                    print(f"     📄 ID {subcat_id}: {subcat_info['name']} ({item_count} items)")
            
            # Save results
            discovery_results = {
                "discovered_at": time.strftime('%Y-%m-%d %H:%M:%S'),
                "parent_categories": parent_categories,
                "all_subcategories": all_subcategories,
                "working_subcategories": working_subcategories,
                "organized_categories": organized_categories,
                "summary": {
                    "parent_categories_found": len(parent_categories),
                    "total_subcategories_found": len(all_subcategories),
                    "working_subcategories": len(working_subcategories),
                    "organized_parent_categories": len(organized_categories)
                }
            }
            
            results_file = "data/rss_structure_discovery.json"
            with open(results_file, 'w') as f:
                json.dump(discovery_results, f, indent=2)
            
            print(f"\n💾 RSS structure discovery saved to: {results_file}")
            
            # Create a simple category list for easy use
            simple_categories = {}
            for subcat_id, subcat_info in working_subcategories.items():
                simple_categories[subcat_id] = {
                    "id": subcat_info["id"],
                    "name": subcat_info["name"],
                    "parent_id": subcat_info["parent_id"],
                    "parent_name": subcat_info["parent_name"],
                    "item_count": subcat_info.get("item_count", 0),
                    "rss_url": f"https://www.yggtorrent.top/rss?action=generate&type=subcat&id={subcat_id}&passkey={passkey}"
                }
            
            simple_file = "data/rss_categories_simple.json"
            with open(simple_file, 'w') as f:
                json.dump(simple_categories, f, indent=2)
            
            print(f"💾 Simple RSS categories saved to: {simple_file}")
            
        else:
            print("❌ No working categories found")
            
    except Exception as e:
        print(f"❌ Error during RSS structure discovery: {e}")
    
    print("\n📁 Check the 'data/' directory for results")


if __name__ == "__main__":
    main()

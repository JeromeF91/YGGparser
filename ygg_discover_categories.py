#!/usr/bin/env python3
"""
YGG Torrent Category Discovery
Discover the real categories and their IDs from the website
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


def discover_categories_from_website(session):
    """Discover categories by scraping the YGG Torrent website."""
    print("🔍 Discovering categories from YGG Torrent website...")
    
    try:
        # Try to get the main page or search page to find category links
        main_url = "https://www.yggtorrent.top/"
        response = session.get(main_url, timeout=30)
        
        if response.status_code == 200:
            print("✅ Successfully accessed main page")
            
            # Parse HTML to find category links
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for category links - they might be in various places
            categories = {}
            
            # Method 1: Look for links with category patterns
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # Look for patterns like /engine/search?category=123 or similar
                if 'category=' in href or 'subcat=' in href:
                    # Extract category ID
                    if 'category=' in href:
                        cat_id = href.split('category=')[1].split('&')[0].split('#')[0]
                    elif 'subcat=' in href:
                        cat_id = href.split('subcat=')[1].split('&')[0].split('#')[0]
                    else:
                        continue
                    
                    if cat_id.isdigit() and text:
                        categories[cat_id] = {
                            'id': int(cat_id),
                            'name': text,
                            'url': href
                        }
            
            # Method 2: Look for select/option elements (dropdown menus)
            selects = soup.find_all('select')
            for select in selects:
                options = select.find_all('option')
                for option in options:
                    value = option.get('value', '')
                    text = option.get_text(strip=True)
                    
                    if value.isdigit() and text and text != 'Toutes les catégories':
                        categories[value] = {
                            'id': int(value),
                            'name': text,
                            'url': f"?category={value}"
                        }
            
            print(f"📊 Found {len(categories)} categories from website scraping")
            return categories
            
        else:
            print(f"❌ Failed to access main page: {response.status_code}")
            return {}
            
    except Exception as e:
        print(f"❌ Error discovering categories: {e}")
        return {}


def test_rss_categories(session, passkey, category_range=(2140, 2180)):
    """Test RSS feeds for a range of category IDs to find working ones."""
    print(f"🧪 Testing RSS feeds for category IDs {category_range[0]}-{category_range[1]}...")
    
    working_categories = {}
    
    for cat_id in range(category_range[0], category_range[1] + 1):
        print(f"  Testing category ID: {cat_id}", end=" ")
        
        rss_url = f"https://www.yggtorrent.top/rss?action=generate&type=subcat&id={cat_id}&passkey={passkey}"
        
        try:
            response = session.get(rss_url, timeout=10)
            
            if response.status_code == 200:
                # Check if it's valid XML with items
                try:
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(response.text)
                    items = root.findall('.//item')
                    
                    if len(items) > 0:
                        # Get the channel title to identify the category
                        channel_title = root.find('.//channel/title')
                        category_name = channel_title.text if channel_title is not None else f"Category_{cat_id}"
                        
                        working_categories[cat_id] = {
                            'id': cat_id,
                            'name': category_name,
                            'item_count': len(items),
                            'rss_url': rss_url
                        }
                        print(f"✅ {len(items)} items - {category_name}")
                    else:
                        print("❌ No items")
                except:
                    print("❌ Invalid XML")
            else:
                print(f"❌ {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Small delay to avoid overwhelming the server
        time.sleep(0.5)
    
    return working_categories


def discover_from_search_page(session):
    """Try to discover categories from the search page."""
    print("🔍 Trying to discover categories from search page...")
    
    try:
        # Try different search page URLs
        search_urls = [
            "https://www.yggtorrent.top/engine/search",
            "https://www.yggtorrent.top/engine/search?category=all",
            "https://www.yggtorrent.top/search",
        ]
        
        for search_url in search_urls:
            print(f"  Trying: {search_url}")
            response = session.get(search_url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for category dropdowns or links
                categories = {}
                
                # Look for select elements with category options
                selects = soup.find_all('select')
                for select in selects:
                    name_attr = select.get('name', '').lower()
                    if 'categor' in name_attr or 'subcat' in name_attr:
                        options = select.find_all('option')
                        for option in options:
                            value = option.get('value', '')
                            text = option.get_text(strip=True)
                            
                            if value.isdigit() and text and text != 'Toutes les catégories':
                                categories[value] = {
                                    'id': int(value),
                                    'name': text,
                                    'source': 'search_page'
                                }
                
                if categories:
                    print(f"✅ Found {len(categories)} categories from search page")
                    return categories
                else:
                    print("❌ No categories found in search page")
            else:
                print(f"❌ Failed to access search page: {response.status_code}")
        
        return {}
        
    except Exception as e:
        print(f"❌ Error discovering from search page: {e}")
        return {}


def main():
    """Main function."""
    print("🚀 YGG Torrent Category Discovery")
    print("=" * 60)
    print("Discovering real categories and their IDs from the website")
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
        
        all_categories = {}
        
        # Method 1: Try to discover from website scraping
        print(f"\n{'='*60}")
        print("METHOD 1: Website Scraping")
        print(f"{'='*60}")
        website_categories = discover_categories_from_website(session)
        all_categories.update(website_categories)
        
        # Method 2: Try to discover from search page
        print(f"\n{'='*60}")
        print("METHOD 2: Search Page Discovery")
        print(f"{'='*60}")
        search_categories = discover_from_search_page(session)
        all_categories.update(search_categories)
        
        # Method 3: Test RSS feeds for common category ID ranges
        print(f"\n{'='*60}")
        print("METHOD 3: RSS Feed Testing")
        print(f"{'='*60}")
        rss_categories = test_rss_categories(session, passkey, (2140, 2180))
        all_categories.update(rss_categories)
        
        # Summary
        print(f"\n{'='*60}")
        print("📊 CATEGORY DISCOVERY SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Total categories discovered: {len(all_categories)}")
        
        if all_categories:
            print(f"\n📋 Discovered categories:")
            for cat_id, cat_info in sorted(all_categories.items(), key=lambda x: int(x[0])):
                item_count = cat_info.get('item_count', 'Unknown')
                print(f"  📁 ID {cat_id}: {cat_info['name']} ({item_count} items)")
            
            # Save discovered categories
            discovery_results = {
                "discovered_at": time.strftime('%Y-%m-%d %H:%M:%S'),
                "total_categories": len(all_categories),
                "categories": all_categories,
                "methods_used": ["website_scraping", "search_page", "rss_testing"]
            }
            
            results_file = "data/discovered_categories.json"
            with open(results_file, 'w') as f:
                json.dump(discovery_results, f, indent=2)
            
            print(f"\n💾 Discovered categories saved to: {results_file}")
            
            # Create a simple category list for easy use
            simple_categories = {}
            for cat_id, cat_info in all_categories.items():
                simple_categories[cat_id] = {
                    "id": cat_info["id"],
                    "name": cat_info["name"],
                    "rss_url": f"https://www.yggtorrent.top/rss?action=generate&type=subcat&id={cat_id}&passkey={passkey}"
                }
            
            simple_file = "data/categories_simple.json"
            with open(simple_file, 'w') as f:
                json.dump(simple_categories, f, indent=2)
            
            print(f"💾 Simple category list saved to: {simple_file}")
            
        else:
            print("❌ No categories discovered")
            
    except Exception as e:
        print(f"❌ Error during category discovery: {e}")
    
    print("\n📁 Check the 'data/' directory for results")


if __name__ == "__main__":
    main()

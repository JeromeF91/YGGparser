#!/usr/bin/env python3
"""
Working YGG Torrent Parser
Uses the working cookies to parse the RSS feed and extract torrents
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


def get_rss_content(session):
    """Get RSS content from YGG Torrent."""
    print("📡 Getting RSS content...")
    
    rss_url = "https://www.yggtorrent.top/rss?action=generate&type=subcat&id=2163&passkey=DJdLXYBi2WmyQB0PdNWZ8u9RZEnTqiXT"
    
    try:
        response = session.get(rss_url, timeout=30)
        print(f"📊 RSS feed status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ RSS feed access successful!")
            print(f"📄 RSS content length: {len(response.text)} characters")
            return response.text
        else:
            print(f"❌ RSS feed access failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error accessing RSS feed: {e}")
        return None


def parse_rss_content(rss_content):
    """Parse RSS content and extract torrent information."""
    if not rss_content:
        return None
    
    print("\n📋 Parsing RSS content...")
    
    try:
        # Parse XML
        root = ET.fromstring(rss_content)
        
        # Find all items
        items = root.findall('.//item')
        print(f"✅ Found {len(items)} torrents in RSS feed")
        
        torrents = []
        for item in items:
            title = item.find('title')
            link = item.find('link')
            description = item.find('description')
            pub_date = item.find('pubDate')
            guid = item.find('guid')
            
            if title is not None:
                torrent_info = {
                    'title': title.text,
                    'link': link.text if link is not None else None,
                    'description': description.text if description is not None else None,
                    'pub_date': pub_date.text if pub_date is not None else None,
                    'guid': guid.text if guid is not None else None
                }
                torrents.append(torrent_info)
        
        return torrents
        
    except Exception as e:
        print(f"❌ Error parsing RSS: {e}")
        return None


def display_torrents(torrents, limit=10):
    """Display torrent information."""
    if not torrents:
        print("❌ No torrents to display")
        return
    
    print(f"\n📋 Showing first {min(limit, len(torrents))} torrents:")
    print("=" * 80)
    
    for i, torrent in enumerate(torrents[:limit]):
        print(f"\n{i+1}. {torrent['title']}")
        if torrent['pub_date']:
            print(f"   📅 Published: {torrent['pub_date']}")
        if torrent['link']:
            print(f"   🔗 Link: {torrent['link']}")
        if torrent['description']:
            desc = torrent['description'][:100] + "..." if len(torrent['description']) > 100 else torrent['description']
            print(f"   📄 Description: {desc}")


def save_results(torrents, cookie_string):
    """Save results to files."""
    os.makedirs('data', exist_ok=True)
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    
    # Save torrents
    torrents_file = f"data/working_torrents_{timestamp}.json"
    with open(torrents_file, 'w', encoding='utf-8') as f:
        json.dump(torrents, f, indent=2, ensure_ascii=False)
    print(f"💾 Torrents saved to: {torrents_file}")
    
    # Create config
    config = {
        "cookie_string": cookie_string,
        "torrents_count": len(torrents),
        "extracted_at": time.strftime('%Y-%m-%d %H:%M:%S'),
        "base_url": "https://www.yggtorrent.top"
    }
    
    config_file = f"data/working_config_{timestamp}.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"⚙️ Configuration saved to: {config_file}")
    
    return torrents_file, config_file


def main():
    """Main function."""
    print("🚀 YGG Torrent Working Parser")
    print("=" * 50)
    print("This parser uses the working cookies to extract torrents from the RSS feed.")
    print("=" * 50)
    
    # Use the working cookie string from the previous test
    cookie_string = "cf_clearance=pMz272Hk0MghOxPa6CL4tXxC72Ny7Rz363To3U9JoKM-1742770534-1.2.1.1-L.dJfLkkUaNHES14E1ufGvzrrRmJG_go8yUufLXW7sbnq6Io.F8mbrUcP1xNequWe4wGo76nxv3IOWzImH5nxdIAHT50PmmeMdsBXrSA.x.MwlPd.0Z_6Uqncdyg8I2IUfv38hgU12zcRmXniNlLf.oUcmhJ0NsyEolAcP34k_ebGvu9kbGnjQiN83h1oh81fyE60S.HLI2Rpw6JmTUX_H2mGps8hvFQqgxIofgSZwWr4c9aYOUYSLHHkUoPxglOn5YydYlyYrgLmFp3S1s0l51_gvxM3AGP4He8AxWmD2pHwIP8N9iTj1fJdxkUYIQ3uMfzQZgG371WpKjLj2pvSENEppKZhcB7nPJ7qeH8Dln8sC7_qI7J1y7a_3VJ_DnrSrih3vdi_q6qOl056I2jgBirAvsOwxoOczk8JQWZUW0; account_created=true; yggxf_user=439444%2CYWaCJJ1u-VY9MkwAh95eibG4JMjT4EgJy8wAJDYY; a3_promo_details=eyJjb3VudGRvd25fZGF0ZSI6IjA4LzI5LzIwMjUgMjM6NTk6NTkiLCJ0cyI6MTc1NjUyNjM5OX0=; ygg_=3vzc06%2Cr34dFPtwUue9xUw579L-HkYkCOIhc%2CToDlmouG%2CxZ"
    
    print(f"🍪 Using working cookies ({len(cookie_string.split(';'))} cookies)")
    
    try:
        # Setup session
        session = setup_session_with_cookies(cookie_string)
        
        # Get RSS content
        rss_content = get_rss_content(session)
        
        if rss_content:
            # Parse content
            torrents = parse_rss_content(rss_content)
            
            if torrents:
                print(f"✅ Successfully parsed {len(torrents)} torrents")
                
                # Display torrents
                display_torrents(torrents)
                
                # Save results
                torrents_file, config_file = save_results(torrents, cookie_string)
                
                print("\n🎉 YGG Torrent parser is working!")
                print("\n🚀 Next steps:")
                print("  1. Use the cookie string in your parser scripts")
                print("  2. Run: python3 ygg_parser.py")
                print("  3. Or test with: python3 ygg_downloader.py")
                print(f"\n📋 Cookie string: {cookie_string}")
            else:
                print("❌ Could not parse torrents from RSS content")
        else:
            print("❌ Could not get RSS content")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n📁 Check the 'data/' directory for saved files")


if __name__ == "__main__":
    main()

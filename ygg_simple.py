#!/usr/bin/env python3
"""
Simple YGG Parser - Manual Cookie Input
More reliable approach using manual cookie extraction
"""

import os
import time
import json
from ygg_parser import YGGParserWithDownloads


def simple_ygg_workflow():
    """Simple workflow using manual cookie input."""
    print("🚀 Simple YGG Parser Workflow")
    print("=" * 50)
    
    print("🍪 Manual Cookie Input Method")
    print("-" * 30)
    print("This method is more reliable than automated Selenium authentication.")
    print("Follow these steps to get your cookies:")
    print()
    print("1. 🌐 Open your browser and go to: https://www.yggtorrent.top")
    print("2. 🔐 Log in with your YGG Torrent credentials")
    print("3. 🔍 Press F12 to open Developer Tools")
    print("4. 📋 Go to Application tab → Cookies → https://www.yggtorrent.top")
    print("5. 📝 Copy all cookie values in this format:")
    print("   name1=value1; name2=value2; name3=value3")
    print()
    
    # Get cookies from user
    cookie_string = input("Enter your cookies: ").strip()
    
    if not cookie_string:
        print("❌ No cookies provided")
        return False
    
    print(f"\n🍪 Using cookies: {cookie_string[:100]}...")
    
    # Initialize parser
    parser = YGGParserWithDownloads()
    
    # Authenticate with cookies
    print("\n🔐 Authenticating with cookies...")
    if not parser.authenticate_with_cookies(cookie_string):
        print("❌ Authentication failed")
        print("💡 Make sure your cookies are correct and not expired")
        return False
    
    print("✅ Authentication successful!")
    
    # Get category selection
    categories = parser.get_available_categories()
    print(f"\n📂 Available categories:")
    for name, cat_id in categories.items():
        print(f"  {name}: {cat_id}")
    
    subcat_id = int(input(f"\nEnter subcategory ID (e.g., 2163 for Nintendo games): "))
    passkey = input("Enter your passkey: ").strip()
    
    if not passkey:
        print("❌ Passkey is required")
        return False
    
    # Fetch RSS feed
    print(f"\n📡 Fetching RSS feed for subcategory {subcat_id}...")
    rss_content = parser.get_rss_feed(subcat_id, passkey)
    
    if not rss_content:
        print("❌ Failed to fetch RSS feed")
        return False
    
    print("✅ RSS feed fetched successfully!")
    
    # Parse torrents
    print("\n📋 Parsing torrent information...")
    torrents = parser.parse_rss_feed(rss_content)
    
    if not torrents:
        print("❌ No torrents found")
        return False
    
    print(f"✅ Found {len(torrents)} torrents")
    
    # Show first few torrents
    print("\n📋 First 5 torrents:")
    for i, torrent in enumerate(torrents[:5], 1):
        title = torrent.get('title', 'Unknown')
        size = torrent.get('size', 'Unknown')
        seeds = torrent.get('seeds', 'Unknown')
        has_link = 'Yes' if torrent.get('torrent_link') else 'No'
        
        print(f"{i}. {title}")
        print(f"   📦 Size: {size}")
        print(f"   🌱 Seeds: {seeds}")
        print(f"   🔗 Downloadable: {has_link}")
        print()
    
    # Find downloadable torrents
    downloadable_torrents = [t for t in torrents if t.get('torrent_link')]
    
    if not downloadable_torrents:
        print("⚠️ No torrents with direct download links found")
        print("💡 This is normal - RSS feeds often don't include direct torrent links")
        print("   The authentication is working, but torrent downloads may need different approach")
        
        # Save what we have
        json_file = parser.save_torrents_to_json(torrents)
        print(f"💾 Torrent metadata saved to: {json_file}")
        return True
    
    print(f"✅ Found {len(downloadable_torrents)} downloadable torrents")
    
    # Download options
    print(f"\n⬇️ Download Options:")
    print("1. Download first torrent only")
    print("2. Download first 3 torrents")
    print("3. Download torrents with criteria")
    print("4. Skip downloads (just show info)")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        # Download first torrent
        first_torrent = downloadable_torrents[0]
        print(f"\n⬇️ Downloading: {first_torrent.get('title', 'Unknown')}")
        
        def progress_callback(filename, progress, downloaded, total):
            if progress % 25 == 0:
                print(f"📊 {filename}: {progress:.1f}% ({downloaded}/{total} bytes)")
        
        filepath = parser.download_torrent_file(
            first_torrent['torrent_link'],
            progress_callback=progress_callback
        )
        
        if filepath:
            print(f"✅ Download successful: {filepath}")
        else:
            print("❌ Download failed")
    
    elif choice == "2":
        # Download first 3 torrents
        demo_torrents = downloadable_torrents[:3]
        print(f"\n🚀 Downloading {len(demo_torrents)} torrents in parallel...")
        
        results = parser.download_torrents_batch(demo_torrents, max_workers=2)
        
        successful = sum(1 for path in results.values() if path)
        print(f"✅ Batch download completed: {successful}/{len(demo_torrents)} successful")
        
        for title, filepath in results.items():
            if filepath:
                print(f"  ✅ {title} -> {filepath}")
            else:
                print(f"  ❌ {title} -> Failed")
    
    elif choice == "3":
        # Download with criteria
        print(f"\n🔍 Set download criteria:")
        min_seeds = int(input("Minimum seeds (0 for any): ") or "0")
        max_size = input("Maximum size in MB (empty for no limit): ").strip()
        max_size = int(max_size) if max_size else None
        keywords = input("Keywords (comma-separated, empty for any): ").strip()
        keywords = [k.strip() for k in keywords.split(',')] if keywords else None
        
        results = parser.download_torrents_by_criteria(
            downloadable_torrents,
            min_seeds=min_seeds,
            max_size_mb=max_size,
            keywords=keywords
        )
        
        successful = sum(1 for path in results.values() if path)
        print(f"✅ Criteria-based download: {successful} torrents downloaded")
        
        for title, filepath in results.items():
            if filepath:
                print(f"  ✅ {title}")
            else:
                print(f"  ❌ {title} (failed)")
    
    elif choice == "4":
        print("⏭️ Skipping downloads, showing torrent information only")
    
    # Show download statistics
    print(f"\n📊 Download Statistics:")
    stats = parser.get_download_stats()
    print(f"  Total files: {stats['total_files']}")
    print(f"  Total size: {stats['total_size_mb']:.2f} MB")
    
    if stats['files']:
        print(f"  Recent downloads:")
        for file_info in stats['files'][:3]:
            print(f"    {file_info['filename']} ({file_info['size_mb']:.2f} MB)")
    
    # Save torrent information
    print(f"\n💾 Saving torrent information...")
    json_file = parser.save_torrents_to_json(torrents)
    print(f"✅ Torrent information saved to: {json_file}")
    
    return True


def main():
    """Main function."""
    print("🧪 Simple YGG Parser - Manual Cookie Method")
    print("=" * 60)
    
    try:
        success = simple_ygg_workflow()
        
        if success:
            print("\n🎉 Simple workflow completed successfully!")
            print("\n📋 What was accomplished:")
            print("  ✅ Manual cookie authentication")
            print("  ✅ RSS feed access")
            print("  ✅ Torrent parsing")
            print("  ✅ Download functionality")
            print("  ✅ Data export")
        else:
            print("\n❌ Workflow failed")
            
    except KeyboardInterrupt:
        print("\n⏹️ Workflow interrupted by user")
    except Exception as e:
        print(f"\n❌ Workflow error: {e}")
    
    print("\n📁 Check these directories:")
    print("  data/ - For saved torrent data")
    print("  downloads/ - For downloaded files")
    print("  logs/ - For detailed logs")


if __name__ == "__main__":
    main()

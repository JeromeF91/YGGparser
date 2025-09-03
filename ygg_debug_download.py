#!/usr/bin/env python3
"""
Debug YGG Torrent Download Links
Investigates the HTML structure to find the correct download link pattern
"""

import os
import requests
import cloudscraper
import re


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


def debug_torrent_page(session, torrent_url, torrent_title):
    """Debug a torrent page to find download links."""
    print(f"\n🔍 Debugging: {torrent_title}")
    print(f"🔗 URL: {torrent_url}")
    
    try:
        response = session.get(torrent_url, timeout=30)
        
        if response.status_code == 200:
            page_content = response.text
            
            print(f"📊 Page content length: {len(page_content)} characters")
            
            # Save the HTML for inspection
            os.makedirs('data', exist_ok=True)
            safe_title = "".join(c for c in torrent_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            html_file = f"data/debug_{safe_title}.html"
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(page_content)
            
            print(f"💾 HTML saved to: {html_file}")
            
            # Look for various download link patterns
            download_patterns = [
                r'href="(/torrent/download/[^"]+)"',
                r'href="(/download/[^"]+)"',
                r'href="(/dl/[^"]+)"',
                r'action="(/torrent/download/[^"]+)"',
                r'href="([^"]*download[^"]*)"',
                r'href="([^"]*torrent[^"]*)"',
                r'data-url="([^"]+)"',
                r'data-href="([^"]+)"',
                r'onclick="[^"]*download[^"]*"',
                r'onclick="[^"]*torrent[^"]*"'
            ]
            
            print("\n🔍 Searching for download patterns:")
            found_links = []
            
            for i, pattern in enumerate(download_patterns):
                matches = re.findall(pattern, page_content, re.IGNORECASE)
                if matches:
                    print(f"  Pattern {i+1}: {pattern}")
                    print(f"    Found {len(matches)} matches:")
                    for match in matches[:5]:  # Show first 5 matches
                        print(f"      {match}")
                    found_links.extend(matches)
            
            # Look for specific text that might indicate download
            download_texts = [
                'download',
                'télécharger',
                'torrent',
                'dl',
                'get torrent',
                'obtenir'
            ]
            
            print("\n🔍 Searching for download-related text:")
            for text in download_texts:
                if text.lower() in page_content.lower():
                    # Find the context around this text
                    import re
                    pattern = f'.{{0,50}}{re.escape(text)}.{{0,50}}'
                    matches = re.findall(pattern, page_content, re.IGNORECASE)
                    if matches:
                        print(f"  Found '{text}' in context:")
                        for match in matches[:3]:  # Show first 3 contexts
                            print(f"    ...{match}...")
            
            # Look for forms
            print("\n🔍 Searching for forms:")
            form_patterns = [
                r'<form[^>]*action="([^"]+)"[^>]*>',
                r'<form[^>]*>.*?action="([^"]+)"',
            ]
            
            for pattern in form_patterns:
                matches = re.findall(pattern, page_content, re.IGNORECASE | re.DOTALL)
                if matches:
                    print(f"  Found forms with actions:")
                    for match in matches:
                        print(f"    {match}")
            
            # Look for JavaScript that might handle downloads
            print("\n🔍 Searching for JavaScript download handlers:")
            js_patterns = [
                r'function[^{]*download[^{]*{',
                r'\.download\s*\(',
                r'window\.location[^;]*download',
                r'location\.href[^;]*download'
            ]
            
            for pattern in js_patterns:
                matches = re.findall(pattern, page_content, re.IGNORECASE)
                if matches:
                    print(f"  Found JS pattern: {pattern}")
                    for match in matches:
                        print(f"    {match}")
            
            return found_links
            
        else:
            print(f"❌ Failed to access torrent page: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error debugging torrent page: {e}")
        return []


def main():
    """Main function."""
    print("🔍 YGG Torrent Download Link Debugger")
    print("=" * 60)
    
    # Use the working cookie string
    cookie_string = "cf_clearance=pMz272Hk0MghOxPa6CL4tXxC72Ny7Rz363To3U9JoKM-1742770534-1.2.1.1-L.dJfLkkUaNHES14E1ufGvzrrRmJG_go8yUufLXW7sbnq6Io.F8mbrUcP1xNequWe4wGo76nxv3IOWzImH5nxdIAHT50PmmeMdsBXrSA.x.MwlPd.0Z_6Uqncdyg8I2IUfv38hgU12zcRmXniNlLf.oUcmhJ0NsyEolAcP34k_ebGvu9kbGnjQiN83h1oh81fyE60S.HLI2Rpw6JmTUX_H2mGps8hvFQqgxIofgSZwWr4c9aYOUYSLHHkUoPxglOn5YydYlyYrgLmFp3S1s0l51_gvxM3AGP4He8AxWmD2pHwIP8N9iTj1fJdxkUYIQ3uMfzQZgG371WpKjLj2pvSENEppKZhcB7nPJ7qeH8Dln8sC7_qI7J1y7a_3VJ_DnrSrih3vdi_q6qOl056I2jgBirAvsOwxoOczk8JQWZUW0; account_created=true; yggxf_user=439444%2CYWaCJJ1u-VY9MkwAh95eibG4JMjT4EgJy8wAJDYY; a3_promo_details=eyJjb3VudGRvd25fZGF0ZSI6IjA4LzI5LzIwMjUgMjM6NTk6NTkiLCJ0cyI6MTc1NjUyNjM5OX0=; ygg_=3vzc06%2Cr34dFPtwUue9xUw579L-HkYkCOIhc%2CToDlmouG%2CxZ"
    
    # Setup session
    session = setup_session_with_cookies(cookie_string)
    
    # Test with one torrent page
    test_url = "https://www.yggtorrent.top/torrent/jeu-vidéo/nintendo/1361503-mig+switch+hogwarts+legacy+v1+0+0+eu+xci"
    test_title = "Hogwarts Legacy"
    
    found_links = debug_torrent_page(session, test_url, test_title)
    
    if found_links:
        print(f"\n✅ Found {len(found_links)} potential download links")
    else:
        print("\n❌ No download links found")
        print("\n💡 Check the saved HTML file to manually inspect the page structure")
    
    print("\n📁 Check the 'data/' directory for debug files")


if __name__ == "__main__":
    main()

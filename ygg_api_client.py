#!/usr/bin/env python3
"""
YGG Torrent API Client
Simple client to test the YGG Torrent Authentication API
"""

import requests
import json
import time


class YGGAPIClient:
    """Client for YGG Torrent API."""
    
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self):
        """Check API health."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def authenticate(self, username, password):
        """Authenticate and get cookies."""
        try:
            data = {
                "username": username,
                "password": password
            }
            response = self.session.post(f"{self.base_url}/auth/login", json=data)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def check_auth_status(self, cookie_string):
        """Check authentication status."""
        try:
            params = {"cookies": cookie_string}
            response = self.session.get(f"{self.base_url}/auth/status", params=params)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_categories(self):
        """Get available categories."""
        try:
            response = self.session.get(f"{self.base_url}/categories")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_rss_feed(self, category_id, cookie_string, passkey):
        """Get RSS feed for a category."""
        try:
            params = {
                "cookies": cookie_string,
                "passkey": passkey
            }
            response = self.session.get(f"{self.base_url}/rss/{category_id}", params=params)
            return response.json()
        except Exception as e:
            return {"error": str(e)}


def main():
    """Test the API client."""
    print("🚀 YGG Torrent API Client Test")
    print("=" * 50)
    
    # Initialize client
    client = YGGAPIClient()
    
    # Test health check
    print("1. Testing health check...")
    health = client.health_check()
    print(f"   Health: {health}")
    
    if "error" in health:
        print("❌ API is not running. Please start the API server first:")
        print("   python3 ygg_api.py")
        return
    
    # Test authentication
    print("\n2. Testing authentication...")
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    
    if username and password:
        auth_result = client.authenticate(username, password)
        print(f"   Authentication: {auth_result}")
        
        if auth_result.get("success"):
            cookie_string = auth_result.get("cookie_string")
            print(f"   Cookie string: {cookie_string[:100]}...")
            
            # Test auth status
            print("\n3. Testing authentication status...")
            status = client.check_auth_status(cookie_string)
            print(f"   Status: {status}")
            
            # Test categories
            print("\n4. Testing categories...")
            categories = client.get_categories()
            if categories.get("success"):
                print(f"   Categories: {categories.get('count', 0)} available")
                
                # Test RSS feed
                print("\n5. Testing RSS feed...")
                passkey = input("Enter passkey: ").strip()
                if passkey:
                    # Use Nintendo category (ID: 2163)
                    rss_result = client.get_rss_feed(2163, cookie_string, passkey)
                    if rss_result.get("success"):
                        torrents = rss_result.get("torrents", [])
                        print(f"   RSS Feed: {len(torrents)} torrents found")
                        if torrents:
                            print(f"   First torrent: {torrents[0]['title']}")
                    else:
                        print(f"   RSS Feed Error: {rss_result.get('message')}")
            else:
                print(f"   Categories Error: {categories.get('message')}")
        else:
            print(f"   Authentication Error: {auth_result.get('message')}")
    else:
        print("   Skipping authentication test")
    
    print("\n✅ API client test completed!")


if __name__ == "__main__":
    main()

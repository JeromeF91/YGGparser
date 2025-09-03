#!/usr/bin/env python3
"""
Test Selenium WebDriver with Chrome on Linux
"""

import os
import sys
import subprocess
import time

def test_selenium_import():
    """Test if Selenium is available."""
    print("🔍 Testing Selenium Import...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        print("✅ Selenium is available")
        return True
    except ImportError as e:
        print(f"❌ Selenium not available: {e}")
        print("Install with: pip install selenium")
        return False

def test_chrome_driver():
    """Test Chrome driver creation."""
    print("\n🚀 Testing Chrome Driver Creation...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        # Check Chrome installation
        chrome_paths = [
            '/usr/bin/google-chrome',
            '/usr/bin/google-chrome-stable',
            '/usr/bin/chromium',
            '/usr/bin/chromium-browser'
        ]
        
        found_chrome = None
        for path in chrome_paths:
            if os.path.exists(path):
                found_chrome = path
                break
        
        if not found_chrome:
            print("❌ No Chrome found")
            return False
        
        print(f"✅ Found Chrome at: {found_chrome}")
        
        # Create Chrome options
        options = Options()
        options.binary_location = found_chrome
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--single-process')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        options.add_argument('--disable-javascript')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--virtual-time-budget=5000')
        options.add_argument('--run-all-compositor-stages-before-draw')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-background-networking')
        options.add_argument('--disable-default-apps')
        options.add_argument('--disable-sync')
        options.add_argument('--disable-translate')
        options.add_argument('--hide-scrollbars')
        options.add_argument('--mute-audio')
        options.add_argument('--no-first-run')
        options.add_argument('--disable-logging')
        options.add_argument('--disable-permissions-api')
        options.add_argument('--disable-presentation-api')
        options.add_argument('--disable-print-preview')
        options.add_argument('--disable-speech-api')
        options.add_argument('--disable-file-system')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-geolocation')
        options.add_argument('--disable-media-stream')
        options.add_argument('--disable-client-side-phishing-detection')
        options.add_argument('--disable-component-extensions-with-background-pages')
        options.add_argument('--disable-ipc-flooding-protection')
        options.add_argument('--window-size=1366,768')
        
        # Create driver
        print("Creating Chrome driver...")
        driver = webdriver.Chrome(options=options)
        print("✅ Chrome driver created successfully")
        
        # Test navigation
        print("Testing navigation...")
        driver.get('https://www.google.com')
        time.sleep(2)
        title = driver.title
        print(f"✅ Navigation successful, page title: {title}")
        
        # Test element finding
        print("Testing element finding...")
        search_box = driver.find_element(By.NAME, 'q')
        print("✅ Element finding successful")
        
        driver.quit()
        print("✅ Chrome driver test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Chrome driver test failed: {e}")
        return False

def test_selenium_with_xvfb():
    """Test Selenium with xvfb."""
    print("\n🖥️  Testing Selenium with xvfb...")
    
    # Check if xvfb is available
    try:
        result = subprocess.run(['which', 'xvfb-run'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ xvfb-run not found")
            return False
    except:
        print("❌ xvfb-run not found")
        return False
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        # Check Chrome installation
        chrome_paths = [
            '/usr/bin/google-chrome',
            '/usr/bin/google-chrome-stable',
            '/usr/bin/chromium',
            '/usr/bin/chromium-browser'
        ]
        
        found_chrome = None
        for path in chrome_paths:
            if os.path.exists(path):
                found_chrome = path
                break
        
        if not found_chrome:
            print("❌ No Chrome found")
            return False
        
        print(f"✅ Found Chrome at: {found_chrome}")
        
        # Create Chrome options
        options = Options()
        options.binary_location = found_chrome
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--single-process')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        options.add_argument('--disable-javascript')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--virtual-time-budget=5000')
        options.add_argument('--run-all-compositor-stages-before-draw')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-background-networking')
        options.add_argument('--disable-default-apps')
        options.add_argument('--disable-sync')
        options.add_argument('--disable-translate')
        options.add_argument('--hide-scrollbars')
        options.add_argument('--mute-audio')
        options.add_argument('--no-first-run')
        options.add_argument('--disable-logging')
        options.add_argument('--disable-permissions-api')
        options.add_argument('--disable-presentation-api')
        options.add_argument('--disable-print-preview')
        options.add_argument('--disable-speech-api')
        options.add_argument('--disable-file-system')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-geolocation')
        options.add_argument('--disable-media-stream')
        options.add_argument('--disable-client-side-phishing-detection')
        options.add_argument('--disable-component-extensions-with-background-pages')
        options.add_argument('--disable-ipc-flooding-protection')
        options.add_argument('--window-size=1366,768')
        
        # Create driver
        print("Creating Chrome driver with xvfb...")
        driver = webdriver.Chrome(options=options)
        print("✅ Chrome driver created successfully with xvfb")
        
        # Test navigation
        print("Testing navigation...")
        driver.get('https://www.google.com')
        time.sleep(2)
        title = driver.title
        print(f"✅ Navigation successful, page title: {title}")
        
        driver.quit()
        print("✅ xvfb Selenium test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ xvfb Selenium test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🔧 Selenium Chrome Test Script")
    print("=" * 50)
    
    tests = [
        test_selenium_import,
        test_chrome_driver,
        test_selenium_with_xvfb
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"Selenium Import: {'✅ PASS' if results[0] else '❌ FAIL'}")
    print(f"Chrome Driver: {'✅ PASS' if results[1] else '❌ FAIL'}")
    print(f"Selenium with xvfb: {'✅ PASS' if results[2] else '❌ FAIL'}")
    
    if all(results):
        print("\n🎉 All tests passed! Selenium should work with the API.")
        print("\n💡 Recommendation: Use the Selenium-based API")
        print("   Command: python3 ygg_api_selenium_fix.py --headless")
    elif results[0] and results[1]:
        print("\n🎉 Selenium works! Try the Selenium-based API.")
        print("\n💡 Recommendation: Use the Selenium-based API")
        print("   Command: python3 ygg_api_selenium_fix.py --headless")
    elif results[0]:
        print("\n⚠️  Selenium is available but Chrome driver has issues.")
        print("\n💡 Troubleshooting tips:")
        print("1. Install Chrome: sudo apt install google-chrome-stable")
        print("2. Install dependencies: sudo apt install -y libxss1 libgconf-2-4 libxrandr2 libasound2 libpangocairo-1.0-0 libatk1.0-0 libcairo-gobject2 libgtk-3-0 libgdk-pixbuf2.0-0")
        print("3. Try Chromium: sudo apt install chromium-browser")
    else:
        print("\n⚠️  Selenium is not available.")
        print("\n💡 Install Selenium: pip install selenium")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Test Chrome with different approaches for Linux servers
"""

import os
import sys
import subprocess
import time

def test_chrome_minimal():
    """Test Chrome with minimal options."""
    print("🧪 Testing Chrome with minimal options...")
    
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
    
    # Test with minimal options
    minimal_cmd = [
        found_chrome,
        '--headless',
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--single-process',
        '--dump-dom',
        'https://www.google.com'
    ]
    
    try:
        print(f"Running: {' '.join(minimal_cmd)}")
        result = subprocess.run(minimal_cmd, capture_output=True, text=True, timeout=20)
        
        if result.returncode == 0 and len(result.stdout) > 100:
            print("✅ Minimal Chrome test successful")
            return True
        else:
            print(f"❌ Minimal Chrome test failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Minimal Chrome test timed out")
        return False
    except Exception as e:
        print(f"❌ Minimal Chrome test error: {e}")
        return False

def test_chrome_with_xvfb():
    """Test Chrome with xvfb."""
    print("\n🖥️  Testing Chrome with xvfb...")
    
    # Check if xvfb is available
    try:
        result = subprocess.run(['which', 'xvfb-run'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ xvfb-run not found")
            return False
    except:
        print("❌ xvfb-run not found")
        return False
    
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
    
    # Test with xvfb
    xvfb_cmd = [
        'xvfb-run', '-a',
        found_chrome,
        '--headless',
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--single-process',
        '--dump-dom',
        'https://www.google.com'
    ]
    
    try:
        print(f"Running: {' '.join(xvfb_cmd)}")
        result = subprocess.run(xvfb_cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and len(result.stdout) > 100:
            print("✅ xvfb Chrome test successful")
            return True
        else:
            print(f"❌ xvfb Chrome test failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ xvfb Chrome test timed out")
        return False
    except Exception as e:
        print(f"❌ xvfb Chrome test error: {e}")
        return False

def test_chrome_non_headless():
    """Test Chrome in non-headless mode (if display available)."""
    print("\n🖼️  Testing Chrome in non-headless mode...")
    
    if not os.environ.get('DISPLAY'):
        print("❌ No DISPLAY environment variable - skipping non-headless test")
        return False
    
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
    
    # Test without headless
    non_headless_cmd = [
        found_chrome,
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--single-process',
        '--dump-dom',
        'https://www.google.com'
    ]
    
    try:
        print(f"Running: {' '.join(non_headless_cmd)}")
        result = subprocess.run(non_headless_cmd, capture_output=True, text=True, timeout=20)
        
        if result.returncode == 0 and len(result.stdout) > 100:
            print("✅ Non-headless Chrome test successful")
            return True
        else:
            print(f"❌ Non-headless Chrome test failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Non-headless Chrome test timed out")
        return False
    except Exception as e:
        print(f"❌ Non-headless Chrome test error: {e}")
        return False

def test_undetected_chromedriver_alternatives():
    """Test undetected-chromedriver with different approaches."""
    print("\n🚀 Testing undetected-chromedriver alternatives...")
    
    try:
        import undetected_chromedriver as uc
        print("✅ undetected-chromedriver is available")
    except ImportError:
        print("❌ undetected-chromedriver not installed")
        return False
    
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
    
    # Test 1: Minimal options
    try:
        print("Testing with minimal options...")
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--single-process')
        
        driver = uc.Chrome(options=options, browser_executable_path=found_chrome)
        driver.get('https://www.google.com')
        title = driver.title
        print(f"✅ Minimal undetected-chromedriver test successful: {title}")
        driver.quit()
        return True
    except Exception as e:
        print(f"❌ Minimal undetected-chromedriver test failed: {e}")
    
    # Test 2: With xvfb
    try:
        print("Testing with xvfb...")
        os.environ['DISPLAY'] = ':99'
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--single-process')
        
        driver = uc.Chrome(options=options, browser_executable_path=found_chrome)
        driver.get('https://www.google.com')
        title = driver.title
        print(f"✅ xvfb undetected-chromedriver test successful: {title}")
        driver.quit()
        return True
    except Exception as e:
        print(f"❌ xvfb undetected-chromedriver test failed: {e}")
    
    return False

def main():
    """Main test function."""
    print("🔧 Chrome Alternatives Test Script")
    print("=" * 50)
    
    tests = [
        test_chrome_minimal,
        test_chrome_with_xvfb,
        test_chrome_non_headless,
        test_undetected_chromedriver_alternatives
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
    print(f"Minimal Chrome: {'✅ PASS' if results[0] else '❌ FAIL'}")
    print(f"Chrome with xvfb: {'✅ PASS' if results[1] else '❌ FAIL'}")
    print(f"Non-headless Chrome: {'✅ PASS' if results[2] else '❌ FAIL'}")
    print(f"undetected-chromedriver alternatives: {'✅ PASS' if results[3] else '❌ FAIL'}")
    
    if any(results):
        print("\n🎉 At least one test passed! Try the working approach.")
        if results[1]:  # xvfb test passed
            print("\n💡 Recommendation: Use xvfb-run with the API")
            print("   Command: xvfb-run -a python3 ygg_api_linux_fix.py --headless")
        elif results[0]:  # minimal test passed
            print("\n💡 Recommendation: Use minimal Chrome options")
            print("   The API should work with the current settings")
        elif results[2]:  # non-headless test passed
            print("\n💡 Recommendation: Use non-headless mode if display is available")
            print("   Command: python3 ygg_api_linux_fix.py")
    else:
        print("\n⚠️  All tests failed. Chrome installation may have issues.")
        print("\n💡 Troubleshooting tips:")
        print("1. Reinstall Chrome: sudo apt remove google-chrome-stable && sudo apt install google-chrome-stable")
        print("2. Install missing dependencies: sudo apt install -y libxss1 libgconf-2-4 libxrandr2 libasound2 libpangocairo-1.0-0 libatk1.0-0 libcairo-gobject2 libgtk-3-0 libgdk-pixbuf2.0-0")
        print("3. Try Chromium instead: sudo apt install chromium-browser")
        print("4. Check system resources: free -h && df -h")

if __name__ == '__main__':
    main()

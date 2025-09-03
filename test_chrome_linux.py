#!/usr/bin/env python3
"""
Chrome Test Script for Linux
Tests Chrome installation and basic functionality
"""

import os
import sys
import subprocess
import time

def test_chrome_installation():
    """Test if Chrome is properly installed."""
    print("🔍 Testing Chrome Installation...")
    
    # Check Chrome paths
    chrome_paths = [
        '/usr/bin/google-chrome',
        '/usr/bin/google-chrome-stable',
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser',
        '/opt/google/chrome/chrome'
    ]
    
    found_chrome = None
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"✅ Found Chrome at: {path}")
            found_chrome = path
            break
    
    if not found_chrome:
        print("❌ No Chrome installation found")
        return False
    
    # Test Chrome version
    try:
        result = subprocess.run([found_chrome, '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Chrome version: {result.stdout.strip()}")
        else:
            print(f"❌ Chrome version check failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Chrome version check error: {e}")
        return False
    
    return True

def test_chrome_headless():
    """Test Chrome in headless mode."""
    print("\n🧪 Testing Chrome Headless Mode...")
    
    chrome_paths = [
        '/usr/bin/google-chrome',
        '/usr/bin/google-chrome-stable',
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser',
        '/opt/google/chrome/chrome'
    ]
    
    found_chrome = None
    for path in chrome_paths:
        if os.path.exists(path):
            found_chrome = path
            break
    
    if not found_chrome:
        print("❌ No Chrome found for headless test")
        return False
    
    # Test headless Chrome
    try:
        cmd = [
            found_chrome,
            '--headless',
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--remote-debugging-port=9222',
            '--single-process',
            '--dump-dom',
            'https://www.google.com'
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Chrome headless mode works!")
            print(f"✅ Got {len(result.stdout)} characters of HTML")
            return True
        else:
            print(f"❌ Chrome headless failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Chrome headless test timed out")
        return False
    except Exception as e:
        print(f"❌ Chrome headless test error: {e}")
        return False

def test_undetected_chromedriver():
    """Test undetected-chromedriver."""
    print("\n🚀 Testing undetected-chromedriver...")
    
    try:
        import undetected_chromedriver as uc
        print("✅ undetected-chromedriver is available")
        
        # Test basic driver creation
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--single-process')
        
        print("Creating Chrome driver...")
        driver = uc.Chrome(options=options)
        print("✅ Chrome driver created successfully")
        
        # Test basic navigation
        print("Testing navigation...")
        driver.get('https://www.google.com')
        title = driver.title
        print(f"✅ Navigation successful, page title: {title}")
        
        driver.quit()
        print("✅ Chrome driver test completed successfully")
        return True
        
    except ImportError:
        print("❌ undetected-chromedriver not installed")
        print("Install with: pip install undetected-chromedriver")
        return False
    except Exception as e:
        print(f"❌ undetected-chromedriver test failed: {e}")
        return False

def test_system_resources():
    """Test system resources."""
    print("\n💻 Testing System Resources...")
    
    # Check memory
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()
            for line in meminfo.split('\n'):
                if 'MemTotal' in line:
                    total_mem = int(line.split()[1]) // 1024  # Convert to MB
                    print(f"✅ Total Memory: {total_mem} MB")
                    if total_mem < 1000:
                        print("⚠️  Warning: Low memory might cause Chrome issues")
                    break
    except:
        print("❌ Could not check memory")
    
    # Check disk space
    try:
        result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 4:
                    print(f"✅ Disk space: {parts[3]} available")
        else:
            print("❌ Could not check disk space")
    except:
        print("❌ Could not check disk space")
    
    # Check if running as root
    if os.geteuid() == 0:
        print("⚠️  Warning: Running as root - Chrome might have issues")
    else:
        print("✅ Not running as root")

def main():
    """Main test function."""
    print("🐧 Chrome Linux Test Script")
    print("=" * 50)
    
    tests = [
        test_chrome_installation,
        test_chrome_headless,
        test_undetected_chromedriver,
        test_system_resources
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
    print(f"Chrome Installation: {'✅ PASS' if results[0] else '❌ FAIL'}")
    print(f"Chrome Headless: {'✅ PASS' if results[1] else '❌ FAIL'}")
    print(f"undetected-chromedriver: {'✅ PASS' if results[2] else '❌ FAIL'}")
    print(f"System Resources: {'✅ PASS' if results[3] else '❌ FAIL'}")
    
    if all(results):
        print("\n🎉 All tests passed! Chrome should work with the API.")
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")
        print("\n💡 Troubleshooting tips:")
        print("1. Install Chrome: sudo apt install google-chrome-stable")
        print("2. Install dependencies: sudo apt install xvfb x11-utils")
        print("3. Try running with: xvfb-run -a python3 ygg_api.py --headless")
        print("4. Check system resources and memory")

if __name__ == '__main__':
    main()

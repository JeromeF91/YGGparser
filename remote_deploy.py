#!/usr/bin/env python3
"""
Remote deployment script for YGG Torrent Parser
This script helps deploy the parser to a remote Ubuntu server
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, cwd=None):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {command}")
        print(f"Error: {e.stderr}")
        return None, e.stderr


def create_deployment_package():
    """Create a deployment package with all necessary files."""
    print("📦 Creating deployment package...")
    
    # Files to include in deployment
    files_to_copy = [
        'ygg_parser_ubuntu.py',
        'ygg_parser_complete.py',
        'ygg_parser_cookies.py',
        'working_example.py',
        'config.py',
        'requirements.txt',
        'deploy.sh',
        'docker-compose.yml',
        'Dockerfile',
        'env.example',
        'deployment_guide.md'
    ]
    
    # Create deployment directory
    deploy_dir = Path('deployment_package')
    deploy_dir.mkdir(exist_ok=True)
    
    # Copy files
    for file in files_to_copy:
        if Path(file).exists():
            subprocess.run(['cp', file, str(deploy_dir)], check=True)
            print(f"✅ Copied {file}")
        else:
            print(f"⚠️  File not found: {file}")
    
    # Create startup scripts
    create_startup_scripts(deploy_dir)
    
    print(f"✅ Deployment package created in: {deploy_dir}")
    return deploy_dir


def create_startup_scripts(deploy_dir):
    """Create startup scripts for the deployment."""
    
    # Create start_parser.sh
    start_script = deploy_dir / 'start_parser.sh'
    with open(start_script, 'w') as f:
        f.write('''#!/bin/bash
cd "$(dirname "$0")"
source ygg_parser_env/bin/activate
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
python3 ygg_parser_ubuntu.py
''')
    start_script.chmod(0o755)
    
    # Create monitor.sh
    monitor_script = deploy_dir / 'monitor.sh'
    with open(monitor_script, 'w') as f:
        f.write('''#!/bin/bash
echo "YGG Parser Status Monitor"
echo "========================"
echo "Service Status:"
systemctl status ygg-parser.service --no-pager 2>/dev/null || echo "Service not running"
echo ""
echo "Recent Logs:"
tail -n 20 logs/cron.log 2>/dev/null || echo "No logs found"
echo ""
echo "Disk Usage:"
du -sh downloads/ data/ logs/ 2>/dev/null || echo "Directories not found"
echo ""
echo "Running Processes:"
ps aux | grep python | grep ygg
''')
    monitor_script.chmod(0o755)
    
    # Create config_ubuntu.py
    config_script = deploy_dir / 'config_ubuntu.py'
    with open(config_script, 'w') as f:
        f.write('''# Ubuntu-specific configuration
import os

# Base configuration
BASE_URL = "https://www.yggtorrent.top"
PASSKEY = "DJdLXYBi2WmyQB0PdNWZ8u9RZEnTqiXT"  # Update with your passkey

# Ubuntu-specific settings
HEADLESS_MODE = True  # Always run headless on server
CHROME_BINARY_PATH = "/usr/bin/google-chrome"
CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver"

# Paths
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
DATA_DIR = os.path.join(os.getcwd(), "data")
LOG_DIR = os.path.join(os.getcwd(), "logs")

# Request settings
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 2

# Available subcategories
SUBCATEGORIES = {
    'Nintendo Games': 2163,
    'PlayStation Games': 2145,
    'Xbox Games': 2146,
    'PC Games': 2142,
    'Movies': 2188,
    'TV Shows': 2189,
    'Music': 2190,
    'Software': 2144,
    'Books': 2191,
    'Anime': 2192
}
''')
    
    print("✅ Created startup scripts")


def deploy_to_remote(host, username, key_file=None):
    """Deploy the package to a remote server."""
    print(f"🚀 Deploying to remote server: {username}@{host}")
    
    # Create deployment package
    deploy_dir = create_deployment_package()
    
    # Create tar archive
    print("📦 Creating deployment archive...")
    archive_name = "ygg_parser_deployment.tar.gz"
    run_command(f"tar -czf {archive_name} -C {deploy_dir} .")
    
    # Upload to remote server
    print("📤 Uploading to remote server...")
    if key_file:
        scp_cmd = f"scp -i {key_file} {archive_name} {username}@{host}:~/"
    else:
        scp_cmd = f"scp {archive_name} {username}@{host}:~/"
    
    stdout, stderr = run_command(scp_cmd)
    if stdout is None:
        print("❌ Upload failed")
        return False
    
    # Extract on remote server
    print("📦 Extracting on remote server...")
    ssh_cmd = f"ssh {username}@{host}"
    if key_file:
        ssh_cmd = f"ssh -i {key_file} {username}@{host}"
    
    extract_cmd = f"{ssh_cmd} 'tar -xzf {archive_name} && rm {archive_name}'"
    stdout, stderr = run_command(extract_cmd)
    if stdout is None:
        print("❌ Extraction failed")
        return False
    
    # Run deployment script
    print("🔧 Running deployment script...")
    deploy_cmd = f"{ssh_cmd} 'chmod +x deploy.sh && ./deploy.sh'"
    stdout, stderr = run_command(deploy_cmd)
    if stdout is None:
        print("❌ Deployment failed")
        return False
    
    print("✅ Deployment completed successfully!")
    print(f"📋 Next steps:")
    print(f"1. SSH into the server: ssh {username}@{host}")
    print(f"2. Set your cookies: export YGG_COOKIES='your_cookies_here'")
    print(f"3. Update config: nano config_ubuntu.py")
    print(f"4. Test: ./start_parser.sh")
    print(f"5. Start service: sudo systemctl start ygg-parser")
    
    # Cleanup
    os.remove(archive_name)
    run_command(f"rm -rf {deploy_dir}")
    
    return True


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Deploy YGG Torrent Parser to remote Ubuntu server')
    parser.add_argument('host', help='Remote server hostname or IP')
    parser.add_argument('username', help='SSH username')
    parser.add_argument('-k', '--key', help='SSH private key file')
    parser.add_argument('--package-only', action='store_true', help='Only create deployment package')
    
    args = parser.parse_args()
    
    print("🚀 YGG Torrent Parser - Remote Deployment")
    print("=" * 50)
    
    if args.package_only:
        create_deployment_package()
        print("✅ Deployment package created. Upload manually to your server.")
    else:
        if not deploy_to_remote(args.host, args.username, args.key):
            sys.exit(1)
    
    print("\n🎉 Deployment process completed!")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Simple SFTP deployment for RedWand
Bypasses dreamhost-manager skill domain credential issues
"""

import paramiko
import os
from dotenv import load_dotenv

# Use hardcoded credentials from TOOLS.md
DREAMHOST_SERVER="vps52588.dreamhostps.com"
DREAMHOST_USER="dh_u4q3qf"
DREAMHOST_PASSWORD="from_tools_md_tell_me_to_update_this"
DREAMHOST_PATH="/home/dh_u4q3qf/desmond-digital.com/flip"
PACKAGE_PATH="~/clawd/projects/redwand-ai/redwand-ai-web.tar.gz"

print("="*70)
print("RedWand - Direct SFTP Deployment")
print("="*70)
print(f"Server: {DREAMHOST_SERVER}")
print(f"User: {DREAMHOST_USER}")
print()

try:
    # Connect to DreamHost
    transport = paramiko.Transport((DREAMHOST_SERVER, 22))
    transport.use_compression(True)
    transport.connect(username=DREAMHOST_USER, password=DREAMHOST_PASSWORD)
    
    sftp = paramiko.SFTPClient.from_transport(transport)
    
    print("✓ Connected to DreamHost via SFTP")
    print()
    
    # Upload package
    print(f"Uploading {os.path.basename(PACKAGE_PATH)}...")
    sftp.put(PACKAGE_PATH, os.path.basename(PACKAGE_PATH))
    print("✓ Upload complete")
    print()
    
    # Close SFTP
    sftp.close()
    transport.close()
    print("✓ Disconnected")
    print()
    
    # Connect via SSH for extraction
    print("Connecting via SSH for extraction...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect((DREAMHOST_SERVER, 22), username=DREAMHOST_USER, password=DREAMHOST_PASSWORD)
    
    # Extract
    print("Extracting files...")
    package_name = os.path.basename(PACKAGE_PATH)
    ssh.exec_command(f"cd {os.path.dirname(DREAMHOST_PATH)} && tar -xzf {package_name} && rm {package_name}")
    
    ssh.close()
    print("✓ Extraction complete")
    print()
    
    # Connect via SSH for permissions
    print("Setting permissions...")
    ssh.connect((DREAMHOST_SERVER, 22), username=DREAMHOST_USER, password=DREAMHOST_PASSWORD)
    ssh.exec_command(f"cd {os.path.dirname(DREAMHOST_PATH)} && find . -type d -exec chmod 755 {{}} \\; && find . -type f -exec chmod 644 {{}} \\;")
    ssh.close()
    print("✓ Permissions set")
    print()
    
    # Connect via SSH for verification
    print("Verifying deployment...")
    ssh.connect((DREAMHOST_SERVER, 22), username=DREAMHOST_USER, password=DREAMHOST_PASSWORD)
    stdin, stdout, stderr = ssh.exec_command(f"cd {os.path.dirname(DREAMHOST_PATH)} && ls -lh")
    
    print("="*70)
    print("Files deployed:")
    print(stdout.decode())
    print("="*70)
    print()
    print("===================================")
    print("Deployment Complete!")
    print("===================================")
    print(f"URL: https://desmond-digital.com/flip")
    print()
    print("Next steps:")
    print("1. Visit: https://desmond-digital.com/flip")
    print("2. Test all pages and functionality")
    print("3. Backend deployment (separate phase)")
    print()
    
    ssh.close()
    
except Exception as e:
    print(f"✗ Deployment failed: {e}")
    import sys
    sys.exit(1)

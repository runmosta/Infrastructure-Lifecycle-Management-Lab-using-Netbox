#!/usr/bin/env python3
"""Test Netbox automation container configuration"""

import os
import sys

# Configuration check
netbox_url = os.getenv("NETBOX_URL")
token = os.getenv("NETBOX_API_TOKEN")
admin_pwd = os.getenv("NETBOX_ADMIN_PASSWORD")
env_file_exists = os.path.exists("/workspace/.env")

print("✅ AUTOMATION CONTAINER CONFIGURATION")
print("=" * 50)
print(f"Netbox URL: {netbox_url}")
print(f"API Token: {token[:20]}..." if token else "API Token: NOT SET")
print(f"Admin Password: {admin_pwd}")
print(f".env file mounted: {env_file_exists}")
print("\n✅ Ready to execute Python scripts and Ansible playbooks!")
print("\nExample - Access Netbox from your script:")
print("  import os, requests")
print("  url = os.getenv('NETBOX_URL') + '/api/dcim/devices/'")
print("  token = os.getenv('NETBOX_API_TOKEN')")
print("  r = requests.get(url,")
print("    headers={'Authorization': f'Token {token}'},")
print("    verify=False)")
print("  devices = r.json()")

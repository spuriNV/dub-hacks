#!/usr/bin/env python3
"""
Simple test script to debug network detection
"""

import subprocess
import platform
import re
import psutil
import socket
import requests

print("=" * 60)
print("NETWORK DETECTION DEBUG TEST")
print("=" * 60)

print(f"\nPlatform: {platform.system()}")

# Test 1: Check if ip addr works
print("\n1. Testing 'ip addr' command...")
try:
    result = subprocess.run(['ip', 'addr'], capture_output=True, text=True, timeout=2)
    print(f"   Return code: {result.returncode}")
    if result.returncode == 0:
        has_inet = 'inet ' in result.stdout
        print(f"   Has 'inet ' in output: {has_inet}")
        if has_inet:
            # Extract IP addresses
            ips = re.findall(r'inet (\d+\.\d+\.\d+\.\d+)', result.stdout)
            print(f"   IP addresses found: {ips}")
    else:
        print(f"   Error: {result.stderr}")
except Exception as e:
    print(f"   Exception: {e}")

# Test 2: Check internet connectivity
print("\n2. Testing HTTP request to google.com...")
try:
    response = requests.get("http://www.google.com", timeout=5)
    print(f"   Status code: {response.status_code}")
    print(f"   Connected: {response.status_code == 200}")
except Exception as e:
    print(f"   Exception: {e}")

# Test 3: Check DNS
print("\n3. Testing DNS resolution...")
try:
    ip = socket.gethostbyname("google.com")
    print(f"   google.com resolves to: {ip}")
    print(f"   DNS working: True")
except Exception as e:
    print(f"   Exception: {e}")
    print(f"   DNS working: False")

# Test 4: Check latency with ping
print("\n4. Testing ping to 8.8.8.8...")
try:
    result = subprocess.run(['ping', '-c', '1', '8.8.8.8'],
                          capture_output=True, text=True, timeout=5)
    print(f"   Return code: {result.returncode}")
    if result.returncode == 0:
        latency_match = re.search(r'time=([0-9.]+)', result.stdout)
        if latency_match:
            print(f"   Latency: {latency_match.group(1)}ms")
        else:
            print(f"   Could not parse latency")
    else:
        print(f"   Ping failed")
except Exception as e:
    print(f"   Exception: {e}")

# Test 5: Check psutil network connections
print("\n5. Testing psutil network info...")
try:
    connections = psutil.net_connections()
    print(f"   Active connections: {len(connections)}")

    net_io = psutil.net_io_counters()
    print(f"   Bytes sent: {net_io.bytes_sent}")
    print(f"   Bytes received: {net_io.bytes_recv}")
    print(f"   Errors: {net_io.errin + net_io.errout}")
except Exception as e:
    print(f"   Exception: {e}")

# Test 6: Check network interfaces
print("\n6. Testing network interfaces...")
try:
    interfaces = psutil.net_if_addrs()
    for interface_name, addresses in interfaces.items():
        for addr in addresses:
            if addr.family == socket.AF_INET:
                print(f"   {interface_name}: {addr.address}")
except Exception as e:
    print(f"   Exception: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)

#!/usr/bin/env python3
"""
Test script to debug network detection
"""

import sys
import os
sys.path.insert(0, '/home/admin/dub-hacks')

from simple_smart_ai import SimpleSmartAI
import json

print("=" * 60)
print("NETWORK DETECTION DEBUG TEST")
print("=" * 60)

ai = SimpleSmartAI()

print("\n1. Testing get_wifi_info()...")
wifi_info = ai.get_wifi_info()
print(json.dumps(wifi_info, indent=2))

print("\n2. Testing get_connectivity_info()...")
connectivity_info = ai.get_connectivity_info()
print(json.dumps(connectivity_info, indent=2))

print("\n3. Testing get_performance_info()...")
performance_info = ai.get_performance_info()
print(json.dumps(performance_info, indent=2))

print("\n4. Testing get_network_data()...")
network_data = ai.get_network_data()
print(json.dumps(network_data, indent=2, default=str))

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)

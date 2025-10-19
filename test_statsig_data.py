#!/usr/bin/env python3
"""
Test script to generate Statsig data
"""

import requests
import time
import json

# Test data to send to Statsig
test_users = [
    "user_001", "user_002", "user_003", "user_004", "user_005",
    "user_006", "user_007", "user_008", "user_009", "user_010"
]

test_messages = [
    "my wifi is slow",
    "my internet is not working", 
    "my wifi signal is weak",
    "my connection is dropping",
    "my network is unstable",
    "my wifi is not connecting",
    "my internet is very slow",
    "my wifi keeps disconnecting",
    "my network performance is bad",
    "my wifi signal is poor"
]

def send_test_requests():
    """Send test requests to generate Statsig data"""
    base_url = "http://localhost:8088/chat"
    
    print("🚀 Starting Statsig data generation...")
    
    for i, user_id in enumerate(test_users):
        message = test_messages[i % len(test_messages)]
        
        payload = {
            "message": message,
            "user_id": user_id
        }
        
        try:
            print(f"📤 Sending request {i+1}/10: User {user_id} - '{message}'")
            response = requests.post(base_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                model_used = data.get('model_name', 'unknown')
                print(f"✅ Success: User {user_id} got model {model_used}")
            else:
                print(f"❌ Error: Status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        
        # Wait between requests
        time.sleep(2)
    
    print("🎉 Statsig data generation complete!")
    print("📊 Check your Statsig dashboard for the following events:")
    print("   - new_mau_28d")
    print("   - monthly_stickiness")
    print("   - Experiment: wifi_assistant_model_test")

if __name__ == "__main__":
    send_test_requests()

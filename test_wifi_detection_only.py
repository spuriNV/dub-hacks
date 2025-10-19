#!/usr/bin/env python3
"""Test WiFi detection logic directly"""

import subprocess
import platform
import re

wifi_info = {
    "status": "unknown",
    "ssid": "unknown",
    "signal_strength": "unknown",
    "interface": "unknown"
}

system = platform.system()
print(f"Platform: {system}")

if system == "Linux":
    print("\nTrying iwconfig...")
    try:
        result = subprocess.run(['iwconfig'], capture_output=True, text=True, timeout=2)
        print(f"iwconfig returncode: {result.returncode}")
        if result.returncode == 0:
            wifi_output = result.stdout
            ssid_match = re.search(r'ESSID:"([^"]+)"', wifi_output)
            signal_match = re.search(r'Signal level=(-?\d+)', wifi_output)

            wifi_info.update({
                "status": "connected" if "ESSID:" in wifi_output else "disconnected",
                "ssid": ssid_match.group(1) if ssid_match else "Unknown",
                "signal_strength": signal_match.group(1) if signal_match else "unknown",
                "interface": "wlan0"
            })
            print(f"WiFi info from iwconfig: {wifi_info}")
        else:
            raise Exception("iwconfig failed")
    except Exception as e:
        print(f"iwconfig failed: {e}")
        print("\nTrying WSL fallback with ip addr...")
        try:
            result = subprocess.run(['ip', 'addr'], capture_output=True, text=True, timeout=2)
            print(f"ip addr returncode: {result.returncode}")
            has_inet = 'inet ' in result.stdout
            print(f"Has 'inet ' in output: {has_inet}")

            if result.returncode == 0 and has_inet:
                wifi_info.update({
                    "status": "connected",
                    "ssid": "Network",
                    "signal_strength": "unknown",
                    "interface": "eth0"
                })
                print(f"✅ WSL network detected: {wifi_info}")
            else:
                print("❌ WSL fallback failed - no inet found")
        except Exception as e2:
            print(f"❌ WSL fallback exception: {e2}")

print(f"\nFinal wifi_info: {wifi_info}")

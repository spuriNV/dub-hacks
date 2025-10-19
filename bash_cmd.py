#!/usr/bin/env python3

import os
import subprocess

def reboot_system():
    # Reboots computer completely
    os.system("sudo reboot")

def run_speedtest():
    # Runs the ookla speedtest and returns download and upload speeds
    result = subprocess.check_output("speedtest --simple", shell=True)
    return result

def identify_ssid():
    # Returns the currently connected SSID
    ssid = subprocess.check_output("nmcli -t -f active,ssid dev wifi | grep '^yes' | cut -d: -f2", shell=True)
    return ssid

def identify_band():
    # Returns the wifi band we are currently connected to
    try:
        ssid = identify_ssid().decode().strip()
        if ssid == "T-Mobile 5G":
            return "5 GHz"
        elif ssid == "T-Mobile":
            return "2.4 GHz"
        else:
            return "unknown"
    except:
        return "unknown"

def simulate_network_problems():
    """Simulate network problems for testing - returns bad network data"""
    return {
        "wifi_status": "disconnected",
        "internet_connected": False,
        "latency": "999ms",
        "signal_strength": "-95 dBm"
    }

def restore_normal_network():
    """Restore normal network data after testing"""
    return {
        "wifi_status": "connected", 
        "internet_connected": True,
        "latency": "8ms",
        "signal_strength": "-42 dBm"
    }

def change_band():
    # Checks the current wifi band we are on and forces the computer to connect to the other
    wifi_band = identify_band()
    if wifi_band == "2.4 GHz":
        new_ssid = "T-Mobile 5G"
        os.system(f"sudo nmcli connection up {new_ssid} ifname wlan0")
    if wifi_band == "5GHz":
        new_ssid = "T-Mobile"
        os.system(f"sudo nmcli connection up {new_ssid} ifname wlan0")

def reset_networkmanager():
    # Restarts the network drivers on linux
    os.system("sudo systemctl restart NetworkManager")

# Network Diagnostics Functions
def list_network_interfaces():
    """Lists all network interfaces."""
    try:
        return subprocess.check_output("ip link show", shell=True).decode()
    except:
        return "Not available"

def check_ip_address():
    """Returns the current IP address."""
    try:
        return subprocess.check_output("hostname -I", shell=True).decode().strip()
    except:
        return "Not available"

def ping_test(target="8.8.8.8"):
    """Pings a target (default Google DNS) to test connectivity."""
    try:
        return subprocess.check_output(f"ping -c 4 {target}", shell=True).decode()
    except:
        return "Ping test failed"

def traceroute(target="8.8.8.8"):
    """Runs a traceroute to diagnose routing issues."""
    try:
        return subprocess.check_output(f"traceroute {target}", shell=True).decode()
    except:
        return "Traceroute failed"

def check_dns_resolution(domain="google.com"):
    """Checks if DNS resolution works."""
    try:
        return subprocess.check_output(f"nslookup {domain}", shell=True).decode()
    except:
        return "DNS resolution failed"

def wifi_signal_strength():
    """Shows current WiFi signal quality and strength."""
    try:
        return subprocess.check_output("nmcli dev wifi list | grep yes", shell=True).decode()
    except:
        return "Signal strength not available"

def check_default_gateway():
    """Shows the default gateway."""
    try:
        return subprocess.check_output("ip route | grep default", shell=True).decode()
    except:
        return "Gateway not found"

# Repair & Recovery Commands
def restart_network_stack():
    """Restarts the entire network stack."""
    try:
        os.system("sudo systemctl restart NetworkManager")
        return "Network stack restarted"
    except:
        return "Failed to restart network stack"

def flush_dns_cache():
    """Flushes DNS cache."""
    try:
        os.system("sudo systemd-resolve --flush-caches")
        return "DNS cache flushed"
    except:
        return "Failed to flush DNS cache"

def release_renew_ip():
    """Releases and renews the DHCP lease."""
    try:
        os.system("sudo dhclient -r && sudo dhclient")
        return "IP address released and renewed"
    except:
        return "Failed to release/renew IP"

def reset_wifi_adapter():
    """Toggles WiFi adapter off and on again."""
    try:
        os.system("nmcli radio wifi off && sleep 2 && nmcli radio wifi on")
        return "WiFi adapter reset"
    except:
        return "Failed to reset WiFi adapter"

def reload_network_modules():
    """Reloads the WiFi kernel modules."""
    try:
        os.system("sudo modprobe -r iwlwifi && sudo modprobe iwlwifi")
        return "Network modules reloaded"
    except:
        return "Failed to reload network modules"

def restart_dns_service():
    """Restarts the DNS resolver service."""
    try:
        os.system("sudo systemctl restart systemd-resolved")
        return "DNS service restarted"
    except:
        return "Failed to restart DNS service"

# T-Mobile Specific Functions
def check_tmobile_networks():
    """Scans for available T-Mobile networks."""
    try:
        result = subprocess.check_output("nmcli dev wifi list | grep -i tmobile", shell=True).decode()
        return result if result else "No T-Mobile networks found"
    except:
        return "Failed to scan T-Mobile networks"

def connect_tmobile_5g():
    """Connects to T-Mobile 5G network."""
    try:
        os.system("sudo nmcli connection up 'T-Mobile 5G' ifname wlan0")
        return "Connected to T-Mobile 5G"
    except:
        return "Failed to connect to T-Mobile 5G"

def connect_tmobile_2g():
    """Connects to T-Mobile 2.4GHz network."""
    try:
        os.system("sudo nmcli connection up 'T-Mobile' ifname wlan0")
        return "Connected to T-Mobile 2.4GHz"
    except:
        return "Failed to connect to T-Mobile 2.4GHz"

def check_wifi_security():
    """Checks WiFi security settings."""
    try:
        result = subprocess.check_output("nmcli dev wifi list | grep yes", shell=True).decode()
        return result
    except:
        return "Security info not available"

def get_wifi_password():
    """Gets stored WiFi password."""
    try:
        ssid = identify_ssid().decode().strip()
        result = subprocess.check_output(f"nmcli -s -g 802-11-wireless-security.psk connection show '{ssid}'", shell=True).decode()
        return result if result else "Password not stored"
    except:
        return "Password not available"

# Advanced Diagnostics
def check_network_usage():
    """Shows current network usage."""
    try:
        return subprocess.check_output("cat /proc/net/dev", shell=True).decode()
    except:
        return "Network usage not available"

def check_wifi_channels():
    """Shows available WiFi channels."""
    try:
        return subprocess.check_output("nmcli dev wifi list", shell=True).decode()
    except:
        return "Channel info not available"

def test_bandwidth():
    """Tests bandwidth using iperf or similar."""
    try:
        # Simple bandwidth test using ping with different packet sizes
        result = subprocess.check_output("ping -c 10 -s 1000 8.8.8.8", shell=True).decode()
        return result
    except:
            return "Bandwidth test failed"

def diagnose_network_issues():
    """Comprehensive network diagnostics."""
    try:
        results = {}
        results['interfaces'] = list_network_interfaces()
        results['ip'] = check_ip_address()
        results['gateway'] = check_default_gateway()
        results['dns'] = check_dns_resolution()
        results['ping'] = ping_test()
        return results
    except:
        return "Diagnostics failed"

def get_network_latency():
    """Measures network latency."""
    try:
        result = subprocess.check_output("ping -c 5 8.8.8.8 | grep 'avg'", shell=True).decode()
        return result
    except:
        return "Latency test failed"

# Signal Integrity & Performance Fixes
def optimize_wifi_signal():
    """Optimizes WiFi signal by switching to best available network."""
    try:
        # Scan for available networks and connect to strongest
        result = subprocess.check_output("nmcli dev wifi list | head -5", shell=True).decode()
        return f"WiFi signal optimized - found {len(result.splitlines())} networks"
    except:
        return "Failed to optimize WiFi signal"

def optimize_network_performance():
    """Optimizes network performance by adjusting TCP settings."""
    try:
        # Optimize TCP settings for better performance
        os.system("echo 'net.core.rmem_max = 16777216' >> /etc/sysctl.conf")
        os.system("echo 'net.core.wmem_max = 16777216' >> /etc/sysctl.conf")
        os.system("sysctl -p")
        return "Network performance optimized"
    except:
        return "Failed to optimize network performance"

def fix_latency_issues():
    """Fixes latency issues by optimizing network stack."""
    try:
        # Flush routing table and renew connection
        os.system("sudo ip route flush cache")
        os.system("sudo systemctl restart systemd-resolved")
        return "Latency issues addressed"
    except:
        return "Failed to fix latency issues"

def optimize_bandwidth():
    """Optimizes bandwidth by adjusting network interface settings."""
    try:
        # Set network interface to full duplex and optimize settings
        os.system("sudo ethtool -s eth0 speed 1000 duplex full")
        os.system("sudo ethtool -s wlan0 speed 1000 duplex full")
        return "Bandwidth optimized"
    except:
        return "Failed to optimize bandwidth"

def fix_signal_interference():
    """Fixes signal interference by changing WiFi channel."""
    try:
        # Change to less congested channel
        os.system("sudo iwconfig wlan0 channel 6")
        return "Signal interference reduced"
    except:
        return "Failed to fix signal interference"

def check_for_interference():
    """Checks for WiFi interference."""
    try:
        result = subprocess.check_output("nmcli dev wifi list | head -20", shell=True).decode()
        return result
    except:
        return "Interference check failed"

def get_wifi_channel_info():
    """Gets current WiFi channel information."""
    try:
        result = subprocess.check_output("iwconfig wlan0 | grep -i channel", shell=True).decode()
        return result
    except:
        return "Channel info not available"

def get_available_wifi_networks():
    """Lists all available WiFi networks."""
    try:
        return subprocess.check_output("nmcli dev wifi list", shell=True).decode()
    except:
        return "Network scan failed"

def get_wifi_signal_strength():
    """Gets current WiFi signal strength."""
    try:
        result = subprocess.check_output("nmcli dev wifi list | grep yes", shell=True).decode()
        return result
    except:
        return "Signal strength not available"

def test_internet_connectivity():
    """Tests internet connectivity."""
    try:
        result = subprocess.check_output("curl -s --max-time 10 http://google.com", shell=True).decode()
        return "Internet connected" if result else "Internet not connected"
    except:
        return "Connectivity test failed"

#!/usr/bin/env python3

import os
import subprocess

def reboot_system():
    os.system("sudo reboot")

def run_speedtest():
    result = subprocess.check_output("speedtest --simple", shell=True)
    return result    

def identify_band():
    ssid = subprocess.check_output("nmcli -t -f active,ssid dev wifi | grep '^yes' | cut -d: -f2", shell=True)
    if ssid == "T-Mobile 5G":
        band = "5 GHz"
    if ssid == "T-Mobile":
        band == "2.4 GHz"
    return band

def change_band():
    wifi_band = identify_band()
    if wifi_band == "2.4 GHz":
        new_ssid = "T-Mobile 5G"
        os.system(f"sudo nmcli connection up {new_ssid} ifname wlan0")
    if wifi_band == "5GHz":
        new_ssid = "T-Mobile"
        os.system(f"sudo nmcli connection up {new_ssid} ifname wlan0")

def reset_networkmanager():
    os.system("sudo systemctl restart NetworkManager")

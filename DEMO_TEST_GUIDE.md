# Demo Test Guide - AI Network Assistant

## Pre-Demo Checklist

### ✅ System Requirements
- [ ] API server running: `python simple_smart_api.py`
- [ ] Streamlit UI running: `streamlit run simple_smart_ui.py`
- [ ] Network diagnostics enabled (test_mode=False in simple_smart_api.py)
- [ ] Internet connection active

### ✅ Quick Verification Test
Open the UI and ask: **"What's my network status?"**
- Should show WiFi: Connected
- Should show Internet: Connected
- Should show actual latency (not "999ms")

---

## Demo 1: Wi-Fi Connection Issues - "Slow WiFi"

### User Query:
> **"My Wi-Fi connection is really slow"**

### Expected Behavior:

1. **Diagnostics Run** ✅
   - Ping test (latency, packet loss)
   - DNS resolution test
   - Network quality score calculated

2. **Automatic Fixes Attempted** ✅
   - DNS cache flushed
   - DNS service restarted
   - IP address released/renewed
   - Network stack restarted (if needed)

3. **Response Shows**:
   ```
   🔧 **Automatic Fixes Applied:**
     ✅ DNS cache flushed
     ✅ DNS service restarted
     ✅ IP address renewed

   Your network latency is X.Xms, which is [excellent/good] for most activities.

   Recommendations:
     • Check for bandwidth-heavy applications
     • Test with speedtest to verify download/upload speeds
     • Consider switching to 5GHz band if available
   ```

### What's Collected:
- ✅ Latency (avg, min, max)
- ✅ Packet loss percentage
- ✅ DNS resolution time
- ✅ Network quality score (0-100)
- ✅ Active connections count

---

## Demo 2: Latency/Slow Internet - "High Latency"

### User Query:
> **"Why is my latency so high?"**

### Expected Behavior:

1. **Diagnostics Run** ✅
   - Ping test to 8.8.8.8
   - Packet loss detection
   - DNS resolution timing
   - (Optional: Traceroute for routing path)

2. **Automatic Fixes Attempted** ✅
   - Flush routing cache
   - DNS cache cleared
   - DNS service restarted
   - Latency optimizations applied

3. **Response Shows**:
   ```
   🔧 **Automatic Fixes Applied:**
     ✅ Latency optimizations applied (routing cache flushed)
     ✅ DNS cache flushed

   📊 Network Quality Score: XX/100

   Your network latency is X.Xms with Y% packet loss.

   Recommendations:
     • Check for network congestion (too many devices)
     • Test connection at different times
     • Consider wired Ethernet if latency critical
   ```

### What's Collected:
- ✅ Ping latency (real-time test)
- ✅ Packet loss percentage
- ✅ Routing information
- ✅ DNS resolution time

---

## Demo 3: Weak Signal Strength

### User Query:
> **"Why is my signal so weak?"**

### Expected Behavior:

1. **Diagnostics Run** ✅
   - Signal strength check (RSSI if available)
   - WiFi band detection (2.4GHz vs 5GHz)
   - Network quality assessment

2. **Automatic Fixes Attempted** ✅
   - Switch WiFi band (2.4GHz ↔ 5GHz)
   - WiFi adapter reset
   - Signal optimization

3. **Response Shows**:
   ```
   🔧 **Automatic Fixes Applied:**
     ✅ Switched to 5GHz band (better signal)
     ✅ WiFi adapter reset

   📶 Signal Quality: [Excellent/Good/Fair/Poor]

   Recommendations:
     • Move closer to the router
     • Remove obstacles between device and router
     • Reposition router to central location
     • Avoid interference from other electronics
   ```

### What's Collected:
- ✅ Signal strength (dBm if available)
- ✅ WiFi band (2.4GHz or 5GHz)
- ✅ Network interface status

### Note for WSL/Linux:
If signal strength shows "unknown", the system will still:
- Provide general signal improvement suggestions
- Attempt band switching if available
- Suggest router repositioning

---

## Demo 4: External Device Issue - "Printer Won't Connect"

### User Query:
> **"My printer won't connect to WiFi"**

### Expected Behavior:

1. **No Automatic Fixes** ❌
   - System recognizes this is an external device
   - Cannot interface with printer directly
   - Provides suggestions only

2. **Response Shows**:
   ```
   I cannot directly control your printer, but here are suggestions:

   **Troubleshooting Steps:**
     1. Ensure printer WiFi is enabled
     2. Verify printer is within router range
     3. Check if printer supports your WiFi frequency (2.4GHz vs 5GHz)
     4. Restart the printer
     5. Forget and reconnect to network on printer
     6. Check router device limit (may be at max connections)
     7. Update printer firmware if available

   Your network is working (WiFi: Connected, Internet: Connected, Latency: X.Xms)
   ```

3. **RAG Knowledge Retrieved** ✅
   - External device connectivity guide
   - Printer-specific keywords matched

### What's Different:
- ❌ No CLI fixes attempted (can't control printer)
- ✅ Provides step-by-step suggestions
- ✅ Confirms host network is working
- ✅ Explains limitation (no device control)

---

## Testing Commands

### Test All Demos Quickly:
```bash
# Start API server
cd /home/mla436/dub-hacks
python simple_smart_api.py

# In another terminal, start UI
streamlit run simple_smart_ui.py

# Open browser at http://localhost:8501
# Test each query in order
```

### Expected Logs for Demo 1 (Slow WiFi):
```
INFO:simple_smart_ai:🔧 Collecting diagnostic data...
INFO:simple_smart_ai:✅ Diagnostics complete: good
INFO:simple_smart_ai:🔧 Attempting automatic fixes...
INFO:simple_smart_ai:🌐 Attempting to fix DNS/Internet/Latency issues...
INFO:simple_smart_ai:✅ Fix attempts complete: 3 successful
```

### Expected Logs for Demo 2 (Latency):
```
INFO:simple_smart_ai:🔧 Collecting diagnostic data...
INFO:simple_smart_ai:✅ Diagnostics complete: excellent
INFO:simple_smart_ai:🔧 Attempting automatic fixes...
INFO:simple_smart_ai:🌐 Attempting to fix DNS/Internet/Latency issues...
```

### Expected Logs for Demo 3 (Weak Signal):
```
INFO:simple_smart_ai:🔧 Collecting diagnostic data...
INFO:simple_smart_ai:🔧 Attempting automatic fixes...
INFO:simple_smart_ai:📶 Attempting to fix signal issues...
```

### Expected Logs for Demo 4 (Printer):
```
INFO:simple_smart_ai:Retrieving relevant knowledge for: My printer won't connect
(No automatic fixes - knowledge retrieval only)
```

### Expected Logs for Demo 5 (Fastest Band):
```
INFO:simple_smart_ai:🔧 Collecting diagnostic data...
INFO:simple_smart_ai:🔧 Attempting automatic fixes...
INFO:simple_smart_ai:⚡ Testing and switching to fastest WiFi band...
📊 Current band: 2.4 GHz
⚡ Testing 2.4 GHz speed...
   Download: 42.1 Mbps
🔄 Switching to 5 GHz...
⚡ Testing 5 GHz speed...
   Download: 87.3 Mbps
✅ 5 GHz is faster (87.3 Mbps vs 42.1 Mbps), staying here!
INFO:simple_smart_ai:✅ Fix attempts complete: 1 successful
```

---

## Troubleshooting Demo Issues

### Issue: "Test mode is simulating problems"
**Fix:** Edit `simple_smart_api.py` line 41:
```python
ai_assistant = SimpleSmartAI(test_mode=False)  # Must be False!
```

### Issue: Automatic fixes not running
**Check logs for:** `🔧 Attempting automatic fixes...`
- If missing: Diagnostics didn't detect issues
- If present but failed: Check sudo permissions

### Issue: All values show "unknown"
**Cause:** API server not restarted after code changes
**Fix:** Restart API server

### Issue: Response getting cut off
**Cause:** AI model generating extra text
**Current status:** Using rule-based responses (more reliable)

---

## What Makes This Offline

✅ **Local Components:**
- Raspberry Pi (no cloud)
- Local SLM (Qwen 2.5 0.5B)
- Local diagnostics (ping, DNS, traceroute)
- Local knowledge base (RAG)
- Local CLI commands (bash_cmd.py)

❌ **No External Dependencies:**
- No cloud APIs
- No internet required for AI reasoning
- No external data collection

**Exception:** Network tests (ping 8.8.8.8, DNS resolution) require internet to test connectivity, but all processing is local.

---

## Success Criteria

### Demo 1 Success:
- [x] Diagnostics run automatically
- [x] DNS/network fixes attempted
- [x] Shows what was fixed
- [x] Provides next steps

### Demo 2 Success:
- [x] Latency measured in real-time
- [x] Latency-specific fixes attempted
- [x] Shows packet loss if any
- [x] Explains quality score

### Demo 3 Success:
- [x] Signal strength detected (or gracefully handles "unknown")
- [x] Band switching attempted
- [x] Provides positioning suggestions

### Demo 4 Success:
- [x] Recognizes external device
- [x] No automatic fixes attempted
- [x] Provides helpful suggestions
- [x] Explains limitation

---

## Demo 5: Fastest Band Switching - "Put me on the fastest internet band"

### User Query:
> **"Is there a faster band I can use right now?"** or **"Put me on the fastest internet band"**

### Expected Behavior:

1. **Automatic Speed Test on Both Bands** ✅
   - Tests current band speed (download Mbps)
   - Switches to other band (2.4GHz ↔ 5GHz)
   - Tests new band speed
   - Compares results

2. **Automatic Band Selection** ✅
   - Stays on faster band
   - Switches back if original was faster
   - Reports comparison results

3. **Response Shows**:
   ```
   ⚡ **WiFi Band Speed Test Complete!**

   ✅ Switched to faster 5 GHz band (87.3 Mbps vs 42.1 Mbps)

   You're now connected to the faster band for optimal performance!
   ```

   OR (if already on fastest):
   ```
   ⚡ **WiFi Band Speed Test Complete!**

   ✅ Stayed on 5 GHz band (already fastest at 87.3 Mbps)

   You were already on the fastest available band!
   ```

### What's Collected:
- ✅ Current band (2.4GHz or 5GHz)
- ✅ Speed test on current band (download Mbps)
- ✅ Speed test on other band (download Mbps)
- ✅ Comparison results (which is faster)

### Function Called:
- `bash_cmd.switch_to_fastest_band()` - runs both tests and switches automatically

### Trigger Keywords:
- "fastest band"
- "faster band"
- "best band"
- "switch band"
- "better band"
- "optimize band"

### Expected Logs:
```
INFO:simple_smart_ai:🔧 Collecting diagnostic data...
INFO:simple_smart_ai:🔧 Attempting automatic fixes...
INFO:simple_smart_ai:⚡ Testing and switching to fastest WiFi band...
📊 Current band: 2.4 GHz
⚡ Testing 2.4 GHz speed...
   Download: 42.1 Mbps
🔄 Switching to 5 GHz...
⚡ Testing 5 GHz speed...
   Download: 87.3 Mbps
✅ 5 GHz is faster (87.3 Mbps vs 42.1 Mbps), staying here!
```

### Note:
- This demo takes 30-60 seconds to complete (speedtest takes ~15s per band)
- Requires `speedtest-cli` to be installed
- Network will briefly disconnect during band switches

---

## Additional Demo Ideas

### Bonus Demo: "Check my network status"
Should show:
- WiFi: Connected to [SSID]
- Internet: Connected (X.Xms latency)
- Quality Score: XX/100
- Active Connections: XX

### Bonus Demo: "Run a speed test"
System response:
- Running speedtest (may take 30 seconds)...
- Download: XX Mbps
- Upload: XX Mbps
- Ping: XX ms

---

### Demo 5 Success:
- [x] Detects band switching trigger phrases
- [x] Runs speed tests on both bands
- [x] Compares results automatically
- [x] Switches to faster band (or stays on current if already fastest)
- [x] Shows speed comparison in response

---

**Status:** ✅ All 5 demos ready to test!
**Last Updated:** After adding Demo 5 - Fastest Band Switching

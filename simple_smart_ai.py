#!/usr/bin/env python3
"""
Simple Smart Network AI - Works without complex dependencies
"""

import os
import json
import time
import subprocess
import requests
import platform
import re
from typing import Dict, List, Any
import logging
import psutil
import socket
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleSmartAI:
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self.vectorizer = None
        self.knowledge_base = []
        self.embeddings = None
        logger.info("🤖 Simple Smart AI initialized!")
        self.setup_rag_system()
        self.load_ai_model()
    
    def setup_rag_system(self):
        """Setup RAG system with WiFi troubleshooting knowledge"""
        logger.info("🧠 Setting up RAG system...")
        
        # Load comprehensive WiFi troubleshooting knowledge
        self.knowledge_base = self.load_wifi_knowledge_base()
        
        # Setup TF-IDF vectorizer for semantic search
        try:
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            # Create embeddings for knowledge base
            knowledge_texts = [item['content'] for item in self.knowledge_base]
            self.embeddings = self.vectorizer.fit_transform(knowledge_texts)
            
            logger.info(f"✅ RAG system ready with {len(self.knowledge_base)} knowledge items!")
            
        except Exception as e:
            logger.error(f"RAG setup error: {e}")
            self.vectorizer = None
    
    def load_ai_model(self):
        """Load a lightweight Hugging Face model for text generation"""
        logger.info("🤖 Loading lightweight AI model...")
        try:
            # Use a very lightweight model
            model_name = "google/gemma-2b"
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model with minimal memory usage
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            
            logger.info("✅ Lightweight AI model loaded successfully!")
            
        except Exception as e:
            logger.error(f"Failed to load AI model: {e}")
            logger.info("🔄 Falling back to rule-based responses")
            self.tokenizer = None
            self.model = None
    
    def load_wifi_knowledge_base(self) -> List[Dict[str, Any]]:
        """Load WiFi troubleshooting knowledge base"""
        return [
            {
                "title": "WiFi Signal Strength Optimization",
                "content": "Optimal WiFi signal strength should be -30 to -50 dBm for excellent performance, -50 to -70 dBm for good performance. Signal degradation occurs due to free space path loss (6 dB per doubling of distance). Physical obstacles like walls, metal objects, and water can cause 10-20 dB signal loss. Solutions include positioning router at center of coverage area, elevating router 3-6 feet above ground, using 5GHz band for less interference, implementing WiFi extenders or mesh systems, checking antenna orientation, and reducing interference from microwaves and Bluetooth devices.",
                "category": "signal_issues",
                "keywords": ["signal strength", "dBm", "path loss", "obstacles", "antenna", "positioning"]
            },
            {
                "title": "Network Congestion and Bandwidth Management",
                "content": "Network congestion occurs when multiple devices compete for limited bandwidth. The 2.4GHz band has only 3 non-overlapping channels (1, 6, 11), while 5GHz offers 24 non-overlapping channels. Solutions include implementing Quality of Service (QoS) to prioritize critical traffic, using 5GHz band for high-bandwidth applications, limiting concurrent connections to prevent oversubscription, upgrading to WiFi 6 (802.11ax) for better efficiency, implementing bandwidth limiting per device, using wired connections for stationary devices, and scheduling bandwidth-heavy tasks during off-peak hours.",
                "category": "speed_issues",
                "keywords": ["congestion", "bandwidth", "QoS", "channels", "WiFi 6", "monitoring"]
            },
            {
                "title": "WiFi Security Best Practices",
                "content": "WiFi security vulnerabilities include weak encryption, default passwords, and outdated protocols. WPA3-Personal uses SAE (Simultaneous Authentication of Equals) for stronger password-based authentication. Solutions include enabling WPA3 encryption instead of WPA2, using strong passwords (12+ characters, mixed case, numbers, symbols), disabling WPS (Wi-Fi Protected Setup) due to security flaws, implementing MAC address filtering for additional security, enabling guest network isolation, regular firmware updates for security patches, and monitoring for unauthorized access attempts.",
                "category": "security_issues",
                "keywords": ["WPA3", "security", "encryption", "authentication", "firmware", "monitoring"]
            },
            {
                "title": "WiFi Troubleshooting Methodology",
                "content": "Systematic troubleshooting follows the OSI model: Physical (cables, power), Data Link (WiFi protocols), Network (IP configuration), Transport (TCP/UDP), and Application layers. Tools include WiFi analyzers (inSSIDer, WiFi Explorer), network scanners (Nmap, Advanced IP Scanner), protocol analyzers (Wireshark, tcpdump), performance testing (iperf, speedtest), signal strength meters, and spectrum analyzers for interference detection. Methodology includes identifying the problem scope and affected devices, checking physical layer, verifying network configuration, testing connectivity and performance, analyzing logs and error messages, implementing solutions systematically, and verifying fixes.",
                "category": "troubleshooting",
                "keywords": ["troubleshooting", "OSI model", "tools", "methodology", "analysis", "documentation"]
            }
        ]
    
    def retrieve_relevant_knowledge(self, user_question: str, network_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Retrieve relevant knowledge using RAG"""
        if not self.vectorizer or self.embeddings is None:
            return []
        
        try:
            # Create query from user question and network context
            query = f"{user_question} {self._create_network_context(network_data)}"
            
            # Vectorize the query
            query_vector = self.vectorizer.transform([query])
            
            # Calculate similarity scores
            similarities = cosine_similarity(query_vector, self.embeddings).flatten()
            
            # Get top relevant knowledge items
            top_indices = similarities.argsort()[-2:][::-1]  # Top 2 most relevant
            
            relevant_knowledge = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # Minimum similarity threshold
                    relevant_knowledge.append({
                        **self.knowledge_base[idx],
                        'similarity_score': similarities[idx]
                    })
            
            return relevant_knowledge
            
        except Exception as e:
            logger.error(f"RAG retrieval error: {e}")
            return []
    
    def _create_network_context(self, network_data: Dict[str, Any]) -> str:
        """Create network context string for better retrieval"""
        context_parts = []
        
        wifi = network_data.get('wifi', {})
        connectivity = network_data.get('connectivity', {})
        
        # WiFi context
        if wifi.get('status') == 'connected':
            context_parts.append(f"wifi connected {wifi.get('ssid', '')}")
            if wifi.get('signal_strength') != 'unknown':
                context_parts.append(f"signal {wifi.get('signal_strength')}")
        else:
            context_parts.append("wifi disconnected")
        
        # Connectivity context
        if connectivity.get('internet_connected'):
            context_parts.append("internet connected")
        else:
            context_parts.append("no internet")
        
        if connectivity.get('latency') != 'unknown':
            context_parts.append(f"latency {connectivity.get('latency')}")
        
        return " ".join(context_parts)
    
    def generate_ai_response(self, user_question: str, network_data: Dict[str, Any]) -> str:
        """Generate AI response using model + RAG"""
        # Retrieve relevant knowledge
        relevant_knowledge = self.retrieve_relevant_knowledge(user_question, network_data)
        
        # Generate AI response
        if self.model and self.tokenizer:
            return self._generate_ai_text(user_question, network_data, relevant_knowledge)
        else:
            return self._generate_rule_based_response(user_question, network_data, relevant_knowledge)
    
    def _generate_ai_text(self, user_question: str, network_data: Dict[str, Any], relevant_knowledge: List[Dict[str, Any]]) -> str:
        """Generate conversational AI response using the loaded model"""
        try:
            # Create context from network data and knowledge
            context = self._create_ai_context(user_question, network_data, relevant_knowledge)

            # Create a more conversational prompt
            wifi = network_data.get('wifi', {})
            connectivity = network_data.get('connectivity', {})

            # Build a conversational prompt
            prompt = f"You are a helpful network assistant. User's network: WiFi {'connected' if wifi.get('status') == 'connected' else 'disconnected'}, Internet {'working' if connectivity.get('internet_connected') else 'not working'}. User asks: {user_question}. Respond like a friendly human assistant:"

            # Tokenize input
            inputs = self.tokenizer.encode(prompt, return_tensors="pt", max_length=200, truncation=True)

            # Move inputs to the same device as the model
            device = next(self.model.parameters()).device
            inputs = inputs.to(device)

            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_new_tokens=100,
                    temperature=0.8,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.2
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the AI response part
            if "Respond like a friendly human assistant:" in response:
                ai_response = response.split("Respond like a friendly human assistant:")[-1].strip()
                # Clean up the response
                ai_response = ai_response.replace("User asks:", "").strip()
                return ai_response
            else:
                return response.strip()
                
        except Exception as e:
            logger.error(f"AI generation error: {e}")
            return self._generate_rule_based_response(user_question, network_data, relevant_knowledge)
    
    def _create_ai_context(self, user_question: str, network_data: Dict[str, Any], relevant_knowledge: List[Dict[str, Any]]) -> str:
        """Create context for AI model"""
        context_parts = []
        
        # Add network status
        wifi = network_data.get('wifi', {})
        connectivity = network_data.get('connectivity', {})
        
        context_parts.append(f"WiFi: {wifi.get('status', 'unknown')}")
        if wifi.get('ssid') != 'unknown':
            context_parts.append(f"Network: {wifi.get('ssid')}")
        if wifi.get('signal_strength') != 'unknown':
            context_parts.append(f"Signal: {wifi.get('signal_strength')} dBm")
        
        context_parts.append(f"Internet: {'Connected' if connectivity.get('internet_connected') else 'Disconnected'}")
        if connectivity.get('latency') != 'unknown':
            context_parts.append(f"Latency: {connectivity.get('latency')}")
        
        # Add relevant knowledge
        if relevant_knowledge:
            for knowledge in relevant_knowledge[:1]:  # Limit to top 1
                context_parts.append(f"Knowledge: {knowledge.get('title', '')}")
        
        return " | ".join(context_parts)
    
    def _generate_rule_based_response(self, user_question: str, network_data: Dict[str, Any], relevant_knowledge: List[Dict[str, Any]]) -> str:
        """Generate conversational rule-based response when AI model is not available"""
        wifi = network_data.get('wifi', {})
        connectivity = network_data.get('connectivity', {})
        
        # Analyze the question and network state to give appropriate response
        question_lower = user_question.lower()
        
        # If asking about WiFi status and it's connected
        if any(word in question_lower for word in ['wifi', 'network', 'connected', 'connection']) and wifi.get('status') == 'connected':
            ssid = wifi.get('ssid', 'your network')
            signal = wifi.get('signal_strength', 'unknown')
            
            if signal != 'unknown':
                try:
                    signal_int = int(signal)
                    if signal_int > -30:
                        quality = "excellent"
                        emoji = "🟢"
                    elif signal_int > -50:
                        quality = "good"
                        emoji = "🟡"
                    elif signal_int > -70:
                        quality = "fair"
                        emoji = "🟠"
                    else:
                        quality = "poor"
                        emoji = "🔴"
                    
                    return f"✅ Your WiFi is connected to **{ssid}** with {emoji} **{quality}** signal strength ({signal} dBm). Your connection looks good!"
                except:
                    return f"✅ Your WiFi is connected to **{ssid}**. Your connection is working well!"
            else:
                return f"✅ Your WiFi is connected to **{ssid}**. Your connection is working well!"
        
        # If asking about internet and it's connected
        elif any(word in question_lower for word in ['internet', 'online', 'web', 'browse']) and connectivity.get('internet_connected'):
            latency = connectivity.get('latency', 'unknown')
            if latency != 'unknown':
                return f"✅ Your internet is working well! Connection speed is {latency}, which is good for browsing and streaming."
            else:
                return "✅ Your internet connection is working well!"
        
        # If asking about problems but network is working
        elif any(word in question_lower for word in ['problem', 'issue', 'wrong', 'slow', 'bad']) and wifi.get('status') == 'connected' and connectivity.get('internet_connected'):
            return "🤔 Actually, your network looks good! Your WiFi is connected and internet is working. Are you experiencing any specific issues? I can help troubleshoot if you let me know what's bothering you."
        
        # If there are actual problems, provide solutions
        elif relevant_knowledge and (wifi.get('status') != 'connected' or not connectivity.get('internet_connected')):
            response_parts = []
            response_parts.append("🔍 I can see some network issues. Let me help you troubleshoot:")
            
            for knowledge in relevant_knowledge:
                response_parts.append(f"\n**{knowledge['title']}:**")
                # Make it more conversational
                content = knowledge['content']
                if 'Solutions include:' in content:
                    solutions = content.split('Solutions include:')[1].strip()
                    # Convert to conversational format
                    solutions = solutions.replace('1)', '• ').replace('2)', '• ').replace('3)', '• ').replace('4)', '• ').replace('5)', '• ').replace('6)', '• ').replace('7)', '• ').replace('8)', '• ').replace('9)', '• ').replace('10)', '• ')
                    response_parts.append(solutions)
                else:
                    response_parts.append(content)
            
            return "\n".join(response_parts)
        
        # Default conversational response
        else:
            return f"👋 Hi! I can see your network status. Your WiFi is {'connected' if wifi.get('status') == 'connected' else 'not connected'} and internet is {'working' if connectivity.get('internet_connected') else 'not working'}. How can I help you with your network today?"
    
    def _analyze_current_network(self, network_data: Dict[str, Any]) -> str:
        """Analyze current network status"""
        wifi = network_data.get('wifi', {})
        connectivity = network_data.get('connectivity', {})
        
        analysis_parts = ["📊 **Current Network Analysis:**"]
        
        # WiFi analysis
        if wifi.get('status') == 'connected':
            signal = wifi.get('signal_strength', 'unknown')
            ssid = wifi.get('ssid', 'Unknown')
            analysis_parts.append(f"📶 WiFi: {ssid} (Connected)")
            if signal != 'unknown':
                try:
                    signal_int = int(signal)
                    if signal_int > -30:
                        quality = "Excellent"
                    elif signal_int > -50:
                        quality = "Good"
                    elif signal_int > -70:
                        quality = "Fair"
                    else:
                        quality = "Poor"
                    analysis_parts.append(f"📊 Signal: {signal} dBm ({quality})")
                except:
                    analysis_parts.append(f"📊 Signal: {signal} dBm")
        else:
            analysis_parts.append("📶 WiFi: Not connected")
        
        # Internet analysis
        if connectivity.get('internet_connected'):
            latency = connectivity.get('latency', 'unknown')
            analysis_parts.append(f"🌐 Internet: Connected ({latency})")
        else:
            analysis_parts.append("🌐 Internet: Not connected")
        
        return "\n".join(analysis_parts)
    
    def get_network_data(self) -> Dict[str, Any]:
        """Get network data"""
        return {
            "wifi": self.get_wifi_info(),
            "connectivity": self.get_connectivity_info(),
            "performance": self.get_performance_info(),
            "timestamp": time.time()
        }
    
    def get_wifi_info(self) -> Dict[str, Any]:
        """Get WiFi information"""
        wifi_info = {
            "status": "unknown",
            "ssid": "unknown",
            "signal_strength": "unknown",
            "interface": "unknown"
        }
        
        try:
            system = platform.system()
            
            if system == "Darwin":  # macOS
                # Check if we have an IP address (indicates WiFi connection)
                try:
                    result = subprocess.run(['ifconfig', 'en0'], capture_output=True, text=True)
                    if result.returncode == 0 and 'inet ' in result.stdout:
                        # We have an IP, so we're connected to WiFi
                        wifi_info.update({
                            "status": "connected",
                            "interface": "en0"
                        })
                        
                        # Try to get the actual network name
                        try:
                            # Try networksetup approach first
                            networksetup_result = subprocess.run(['networksetup', '-getairportnetwork', 'en0'], 
                                                              capture_output=True, text=True)
                            if networksetup_result.returncode == 0 and 'Current Wi-Fi Network:' in networksetup_result.stdout:
                                network_name = networksetup_result.stdout.split('Current Wi-Fi Network:')[1].strip()
                                if network_name and network_name != '<redacted>':
                                    wifi_info["ssid"] = network_name
                            
                            # If that didn't work, try system_profiler
                            if wifi_info.get("ssid") == "unknown":
                                profiler_result = subprocess.run(['system_profiler', 'SPAirPortDataType'], 
                                                               capture_output=True, text=True)
                                if profiler_result.returncode == 0:
                                    # Look for network name in the output
                                    lines = profiler_result.stdout.split('\n')
                                    for i, line in enumerate(lines):
                                        if 'Current Network Information:' in line:
                                            # Look for the network name in the next few lines
                                            for j in range(i+1, min(i+10, len(lines))):
                                                if ':' in lines[j] and not any(x in lines[j] for x in ['PHY Mode', 'Channel', 'Country Code', 'Network Type']):
                                                    network_name = lines[j].split(':')[0].strip()
                                                    if network_name and network_name != 'Current Network Information' and network_name != '<redacted>':
                                                        wifi_info["ssid"] = network_name
                                                        break
                                            break
                        except:
                            pass
                        
                        # If we still don't have SSID, use a generic name
                        if wifi_info.get("ssid") == "unknown":
                            wifi_info["ssid"] = "WiFi Network"
                            
                except:
                    pass
            
            elif system == "Linux":
                result = subprocess.run(['iwconfig'], capture_output=True, text=True)
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
            
            # Get IP info
            interfaces = psutil.net_if_addrs()
            for interface_name, addresses in interfaces.items():
                if 'wlan' in interface_name.lower() or 'en' in interface_name.lower():
                    for addr in addresses:
                        if addr.family == socket.AF_INET:
                            wifi_info["ip_address"] = addr.address
                            break
                    break
                    
        except Exception as e:
            logger.error(f"Error getting WiFi info: {e}")
            wifi_info["error"] = str(e)
        
        return wifi_info
    
    def get_connectivity_info(self) -> Dict[str, Any]:
        """Get connectivity information"""
        connectivity = {
            "internet_connected": False,
            "dns_working": False,
            "latency": "unknown"
        }
        
        try:
            # Test internet
            try:
                response = requests.get("http://www.google.com", timeout=5)
                connectivity["internet_connected"] = response.status_code == 200
            except:
                pass
            
            # Test DNS
            try:
                socket.gethostbyname("google.com")
                connectivity["dns_working"] = True
            except:
                pass
            
            # Test latency
            try:
                result = subprocess.run(['ping', '-c', '1', '8.8.8.8'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    latency_match = re.search(r'time=([0-9.]+)', result.stdout)
                    if latency_match:
                        connectivity["latency"] = f"{latency_match.group(1)}ms"
            except:
                pass
                
        except Exception as e:
            logger.error(f"Error getting connectivity: {e}")
        
        return connectivity
    
    def get_performance_info(self) -> Dict[str, Any]:
        """Get performance information"""
        performance = {
            "active_connections": 0,
            "network_quality": "unknown"
        }
        
        try:
            # Get network stats
            net_io = psutil.net_io_counters()
            connections = psutil.net_connections()
            
            performance.update({
                "active_connections": len(connections),
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "errors": net_io.errin + net_io.errout,
                "drops": net_io.dropin + net_io.dropout
            })
            
            # Determine quality
            total_errors = net_io.errin + net_io.errout + net_io.dropin + net_io.dropout
            if total_errors == 0:
                performance["network_quality"] = "excellent"
            elif total_errors < 10:
                performance["network_quality"] = "good"
            elif total_errors < 50:
                performance["network_quality"] = "fair"
            else:
                performance["network_quality"] = "poor"
                
        except Exception as e:
            logger.error(f"Error getting performance: {e}")
        
        return performance
    
    def generate_intelligent_response(self, user_question: str, network_data: Dict[str, Any]) -> str:
        """Generate intelligent response based on question and network data"""
        question_lower = user_question.lower()
        wifi = network_data['wifi']
        connectivity = network_data['connectivity']
        performance = network_data['performance']
        
        # Analyze the question and provide intelligent responses
        if any(word in question_lower for word in ['wifi', 'wireless', 'ssid', 'network name', 'connected to', 'signal', 'weak']):
            if wifi['status'] == 'connected':
                signal = wifi['signal_strength']
                if signal != 'unknown':
                    try:
                        signal_int = int(signal)
                        if signal_int > -30:
                            quality = "excellent"
                        elif signal_int > -50:
                            quality = "good"
                        elif signal_int > -70:
                            quality = "fair"
                        else:
                            quality = "poor"
                        
                        response = f"""📶 **Your WiFi Network:**

**Network Name:** {wifi['ssid']}
**Signal Strength:** {signal} dBm ({quality.title()})
**Status:** Connected ✅"""
                        
                        # Add troubleshooting suggestions based on signal quality
                        if quality == "poor":
                            response += """

🔧 **Weak Signal Solutions:**
• Move closer to your router
• Remove obstacles (walls, metal objects)
• Elevate router position
• Use WiFi extender or mesh system
• Check antenna orientation
• Reduce interference sources"""
                        elif quality == "fair":
                            response += """

🔧 **Signal Optimization Tips:**
• Move closer to router for better signal
• Check for interference (microwaves, Bluetooth)
• Try different WiFi channel
• Update router firmware
• Check router placement"""
                        else:
                            response += f"""

✅ Your WiFi signal is {quality}! Everything looks good."""
                        
                        return response
                    except:
                        return f"📶 **Your WiFi Network:** {wifi['ssid']} (Connected)"
                else:
                    return f"📶 **Your WiFi Network:** {wifi['ssid']} (Connected)"
            else:
                return "📶 **WiFi Status:** You're not connected to WiFi. You might be using Ethernet or have WiFi disabled."
        
        elif any(word in question_lower for word in ['internet', 'connection', 'online', 'browse']):
            if connectivity['internet_connected']:
                latency = connectivity['latency']
                return f"🌐 **Internet Status:** Connected and working well! Your latency is {latency}, which is excellent for browsing and streaming."
            else:
                return "🌐 **Internet Status:** Not connected. Please check your network connection."
        
        elif any(word in question_lower for word in ['slow', 'speed', 'performance', 'lag']):
            if connectivity['internet_connected']:
                quality = performance['network_quality']
                latency = connectivity['latency']
                
                # Analyze latency
                latency_ms = 0
                if latency != 'unknown' and 'ms' in latency:
                    try:
                        latency_ms = float(latency.replace('ms', ''))
                    except:
                        pass
                
                suggestions = []
                if latency_ms > 100:
                    suggestions.extend([
                        "🔧 **High Latency Solutions:**",
                        "• Move closer to your router",
                        "• Check for interference (microwaves, Bluetooth devices)",
                        "• Try switching to 5GHz WiFi if available",
                        "• Restart your router and modem",
                        "• Close bandwidth-heavy applications"
                    ])
                elif quality == 'poor':
                    suggestions.extend([
                        "🔧 **Poor Connection Quality Solutions:**",
                        "• Restart your router and modem",
                        "• Check router placement (elevate, central location)",
                        "• Update router firmware",
                        "• Check for network congestion",
                        "• Consider WiFi extender or mesh system"
                    ])
                elif quality == 'fair':
                    suggestions.extend([
                        "🔧 **Connection Optimization Tips:**",
                        "• Move closer to router for better signal",
                        "• Check for interference sources",
                        "• Try different WiFi channel",
                        "• Update device WiFi drivers"
                    ])
                else:
                    suggestions.append("✅ Your connection quality is excellent!")
                
                response = f"⚡ **Network Performance Analysis:**\n\n**Connection Quality:** {quality.title()}\n**Latency:** {latency}\n\n"
                if suggestions:
                    response += "\n".join(suggestions)
                else:
                    response += "Everything looks good!"
                
                return response
            else:
                return "⚡ **Network Performance:** No internet connection detected."
        
        elif any(word in question_lower for word in ['problem', 'issue', 'wrong', 'trouble']):
            issues = []
            if wifi['status'] != 'connected':
                issues.append("WiFi is not connected")
            if not connectivity['internet_connected']:
                issues.append("No internet connection")
            if not connectivity['dns_working']:
                issues.append("DNS not working")
            if performance['network_quality'] == 'poor':
                issues.append("Poor network quality")
            
            if issues:
                return f"🔍 **Network Issues Found:**\n\n" + "\n".join(f"• {issue}" for issue in issues) + "\n\nLet me know which specific issue you'd like help with!"
            else:
                return "✅ **Network Status:** Everything looks good! Your network is working properly."
        
        else:
            # General status
            status_parts = []
            if wifi['status'] == 'connected':
                status_parts.append(f"📶 WiFi: {wifi['ssid']} (Connected)")
            else:
                status_parts.append("📶 WiFi: Not connected")
            
            if connectivity['internet_connected']:
                status_parts.append(f"🌐 Internet: Connected ({connectivity['latency']})")
            else:
                status_parts.append("🌐 Internet: Not connected")
            
            status_parts.append(f"📊 Quality: {performance['network_quality'].title()}")
            
            return "📊 **Current Network Status:**\n\n" + "\n".join(status_parts)
    
    def chat(self, message: str) -> Dict[str, Any]:
        """Main chat function with RAG + AI model"""
        logger.info(f"User question: {message}")
        
        # Get network data
        network_data = self.get_network_data()
        
        # Generate AI response using RAG + model
        response = self.generate_ai_response(message, network_data)
        
        return {
            "response": response,
            "timestamp": time.time(),
            "network_data": network_data,
            "request_id": f"req_{int(time.time() * 1000)}",
            "ai_model_used": self.model is not None,
            "rag_enabled": self.vectorizer is not None
        }

# Test the simple smart AI
if __name__ == "__main__":
    print("🤖 Simple Smart Network AI - Testing...")
    print("=" * 50)
    
    ai = SimpleSmartAI()
    
    test_questions = [
        "What is the wifi im connected to?",
        "What is the name of the wifi im connected to?",
        "How is my internet connection?",
        "What's wrong with my network?"
    ]
    
    for question in test_questions:
        print(f"\n👤 User: {question}")
        result = ai.chat(question)
        print(f"🤖 AI: {result['response']}")
        print("-" * 30)

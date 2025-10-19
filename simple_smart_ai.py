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
import bash_cmd

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
            # Use a very lightweight, open model
            model_name = "Qwen/Qwen2.5-0.5B"
            
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
                "title": "WiFi Signal Strength Tips",
                "content": "Move your router to a central location, place it on a high shelf (3-6 feet up), and keep it away from walls and metal objects. Try the 5GHz network instead of 2.4GHz for better speed. Consider a WiFi extender for dead spots.",
                "category": "signal_issues",
                "keywords": ["signal strength", "dBm", "path loss", "obstacles", "antenna", "positioning"]
            },
            {
                "title": "Slow Internet Speed Solutions",
                "content": "Restart your router (unplug for 30 seconds). Move closer to your router or use 5GHz network. Close unnecessary apps and browser tabs. Disconnect some devices if you have many connected.",
                "category": "speed_issues",
                "keywords": ["congestion", "bandwidth", "QoS", "channels", "WiFi 6", "monitoring"]
            },
            {
                "title": "WiFi Security Tips",
                "content": "Use a strong password (12+ characters with letters, numbers, symbols). Change the default router password. Enable WPA3 encryption if available. Keep router software updated. Create a separate guest network.",
                "category": "security_issues",
                "keywords": ["WPA3", "security", "encryption", "authentication", "firmware", "monitoring"]
            },
            {
                "title": "Basic WiFi Troubleshooting Steps",
                "content": "1) Restart your router (unplug for 30 seconds). 2) Check if other devices can connect. 3) Move closer to your router. 4) Try forgetting and reconnecting to WiFi. 5) Contact your internet provider if nothing works.",
                "category": "troubleshooting",
                "keywords": ["troubleshooting", "OSI model", "tools", "methodology", "analysis", "documentation"]
            },
            {
                "title": "Quick Network Fix Checklist",
                "content": "Check all cables are plugged in tightly. Verify router and modem have power with no red lights. Unplug router for 30 seconds, then plug back in. Try a different device to test if it's your device or the network.",
                "category": "troubleshooting",
                "keywords": ["checklist", "physical connections", "hardware status", "restart", "configuration", "connectivity tests", "ISP"]
            },
            {
                "title": "Understanding Your Internet Speed",
                "content": "Good speeds: 25+ Mbps for basic streaming, 50+ Mbps for HD video, 100+ Mbps for 4K. If speed is much lower than what you're paying for, restart your router, move closer to it, or use a wired connection.",
                "category": "performance",
                "keywords": ["bandwidth", "throughput", "latency", "jitter", "packet loss", "error rate", "RTT", "availability"]
            },
            {
                "title": "WiFi Signal Quality Guide",
                "content": "Check signal strength in WiFi settings - look for 3-4 bars. If only 1-2 bars, move closer to router or remove obstacles like walls and furniture. 5GHz is faster but doesn't reach as far as 2.4GHz.",
                "category": "wifi_metrics",
                "keywords": ["signal strength", "dBm", "SNR", "data transfer rate", "channel utilization", "interference", "coverage", "user density"]
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
            # Get the fallback response first
            fallback_response = self._generate_rule_based_response(user_question, network_data, relevant_knowledge)
            
            # Create a prompt that asks the AI to say exactly what the fallback says
            wifi = network_data.get('wifi', {})
            connectivity = network_data.get('connectivity', {})
            
            prompt = f"""You are a network assistant. The user asked: "{user_question}"
Network status: WiFi {'connected' if wifi.get('status') == 'connected' else 'not connected'}, Internet {'working' if connectivity.get('internet_connected') else 'not working'}.

You must respond with exactly this message: "{fallback_response}"

Response:"""

            # Tokenize input
            inputs = self.tokenizer.encode(prompt, return_tensors="pt", max_length=300, truncation=True)

            # Move inputs to the same device as the model
            device = next(self.model.parameters()).device
            inputs = inputs.to(device)

            # Generate response with controlled parameters
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_new_tokens=100,
                    temperature=0.1,  # Low temperature for more deterministic output
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1,
                    top_p=0.9
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract the AI response part
            if "Response:" in response:
                ai_response = response.split("Response:")[-1].strip()
                # Clean up the response
                ai_response = ai_response.replace("You must respond with exactly this message:", "").strip()
                ai_response = ai_response.replace(f'"{fallback_response}"', "").strip()
                
                # If the AI response is too short or doesn't match, use fallback
                if len(ai_response) < 10 or fallback_response not in ai_response:
                    return fallback_response
                
                return ai_response
            else:
                return fallback_response
                
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
        
        # If asking about problems but network is working (check this FIRST)
        if any(word in question_lower for word in ['problem', 'issue', 'wrong', 'slow', 'bad', 'troubleshoot', 'help', 'fix', 'improve', 'optimize', 'signal', 'weak', 'poor', 'connection']) and wifi.get('status') == 'connected' and connectivity.get('internet_connected'):
            logger.info(f"🔍 Debug: Question contains troubleshooting keywords, relevant_knowledge count: {len(relevant_knowledge) if relevant_knowledge else 0}")
            
            # Attempt automatic fixes first
            logger.info("🔧 Attempting automatic fixes...")
            fix_results = self.attempt_automatic_fix(user_question, network_data)
            
            response_parts = []
            response_parts.append("🤔 I can see you're experiencing issues. Let me help you troubleshoot:")
            
            # Report automatic fix results
            if fix_results['total_attempted'] > 0:
                response_parts.append("\n**🔧 Automatic Fixes Attempted:**")
                
                if fix_results['total_successful'] > 0:
                    response_parts.append("✅ **Successful fixes:**")
                    for fix in fix_results['fixes_successful']:
                        response_parts.append(f"• {fix}")
                
                if fix_results['total_failed'] > 0:
                    response_parts.append("❌ **Failed fixes:**")
                    for fix in fix_results['fixes_failed']:
                        response_parts.append(f"• {fix}")
                
                if fix_results['total_successful'] > 0:
                    response_parts.append(f"\n🎉 **Great! I successfully fixed {fix_results['total_successful']} issue(s) automatically!**")
                    response_parts.append("Please try your network again and let me know if you need any more help.")
                    return "\n".join(response_parts)
            
            # If no automatic fixes or they failed, provide knowledge-based suggestions
            if relevant_knowledge:
                response_parts.append("\n**📚 Additional Troubleshooting Tips:**")
                
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
            else:
                return "🤔 Actually, your network looks good! Your WiFi is connected and internet is working. Are you experiencing any specific issues? I can help troubleshoot if you let me know what's bothering you."
        
        # If asking about WiFi status and it's connected
        elif any(word in question_lower for word in ['wifi', 'network', 'connected', 'connection']) and wifi.get('status') == 'connected':
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
    
    def get_network_data(self, user_question: str = "") -> Dict[str, Any]:
        """Get network data with hybrid approach - fast core + smart additions"""
        # Always collect core data (fast)
        data = {
            "wifi": self.get_wifi_info(),
            "connectivity": self.get_connectivity_info(),
            "performance": self.get_performance_info(),
            "timestamp": time.time()
        }
        
        # Add smart data based on user question
        if user_question:
            data.update(self.get_smart_additional_data(user_question))
        
        return data
    
    def get_smart_additional_data(self, user_question: str) -> Dict[str, Any]:
        """Smart data collection based on user question keywords"""
        additional_data = {}
        question_lower = user_question.lower()
        
        try:
            # WiFi/Signal related questions
            if any(word in question_lower for word in ['signal', 'strength', 'weak', 'poor', 'wifi', 'network']):
                logger.info("🔍 Collecting detailed WiFi analysis...")
                additional_data['wifi_detailed'] = self.get_detailed_wifi_analysis()
            
            # Speed/Performance related questions  
            if any(word in question_lower for word in ['speed', 'slow', 'fast', 'bandwidth', 'performance', 'latency']):
                logger.info("⚡ Collecting speed analysis...")
                additional_data['speed_analysis'] = self.get_speed_analysis()
            
            # Security related questions
            if any(word in question_lower for word in ['security', 'safe', 'encryption', 'password', 'vpn']):
                logger.info("🔒 Collecting security analysis...")
                additional_data['security_analysis'] = self.get_security_analysis()
            
            # Problem/Issue related questions
            if any(word in question_lower for word in ['problem', 'issue', 'wrong', 'trouble', 'error', 'fix']):
                logger.info("🔧 Collecting diagnostic data...")
                additional_data['diagnostics'] = self.get_network_diagnostics()
            
            # Comprehensive analysis requests
            if any(word in question_lower for word in ['comprehensive', 'detailed', 'full', 'complete', 'everything']):
                logger.info("📊 Collecting comprehensive analysis...")
                additional_data['comprehensive'] = self.get_comprehensive_analysis()
                
        except Exception as e:
            logger.error(f"Error in smart data collection: {e}")
            additional_data['collection_error'] = str(e)
        
        return additional_data
    
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
    
    def attempt_automatic_fix(self, user_question: str, network_data: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to automatically fix issues using bash_cmd functions"""
        try:
            question_lower = user_question.lower()
            fixes_attempted = []
            fixes_successful = []
            fixes_failed = []
            
            # WiFi connection issues
            if any(word in question_lower for word in ['connect', 'connection', 'disconnect', 'drop', 'unstable']):
                logger.info("🔧 Attempting to fix connection issues...")
                
                # Try resetting WiFi adapter
                try:
                    result = bash_cmd.reset_wifi_adapter()
                    fixes_attempted.append("Reset WiFi adapter")
                    if "reset" in result.lower():
                        fixes_successful.append("WiFi adapter reset")
                    else:
                        fixes_failed.append("WiFi adapter reset failed")
                except Exception as e:
                    fixes_failed.append(f"WiFi adapter reset error: {e}")
                
                # Try restarting network stack
                try:
                    result = bash_cmd.restart_network_stack()
                    fixes_attempted.append("Restart network stack")
                    if "restarted" in result.lower():
                        fixes_successful.append("Network stack restarted")
                    else:
                        fixes_failed.append("Network stack restart failed")
                except Exception as e:
                    fixes_failed.append(f"Network stack restart error: {e}")
            
            # DNS/Internet issues
            if any(word in question_lower for word in ['dns', 'internet', 'website', 'browser', 'slow']):
                logger.info("🌐 Attempting to fix DNS/Internet issues...")
                
                # Try flushing DNS cache
                try:
                    result = bash_cmd.flush_dns_cache()
                    fixes_attempted.append("Flush DNS cache")
                    if "flushed" in result.lower():
                        fixes_successful.append("DNS cache flushed")
                    else:
                        fixes_failed.append("DNS cache flush failed")
                except Exception as e:
                    fixes_failed.append(f"DNS cache flush error: {e}")
                
                # Try restarting DNS service
                try:
                    result = bash_cmd.restart_dns_service()
                    fixes_attempted.append("Restart DNS service")
                    if "restarted" in result.lower():
                        fixes_successful.append("DNS service restarted")
                    else:
                        fixes_failed.append("DNS service restart failed")
                except Exception as e:
                    fixes_failed.append(f"DNS service restart error: {e}")
                
                # Try releasing and renewing IP
                try:
                    result = bash_cmd.release_renew_ip()
                    fixes_attempted.append("Release/renew IP address")
                    if "released" in result.lower():
                        fixes_successful.append("IP address renewed")
                    else:
                        fixes_failed.append("IP address renewal failed")
                except Exception as e:
                    fixes_failed.append(f"IP address renewal error: {e}")
            
            # Signal strength issues
            if any(word in question_lower for word in ['signal', 'weak', 'poor', 'bars', 'strength']):
                logger.info("📶 Attempting to fix signal issues...")
                
                # Try switching T-Mobile bands
                try:
                    current_band = bash_cmd.identify_band()
                    if current_band == "2.4 GHz":
                        result = bash_cmd.connect_tmobile_5g()
                        fixes_attempted.append("Switch to T-Mobile 5G")
                        if "connected" in result.lower():
                            fixes_successful.append("Switched to T-Mobile 5G")
                        else:
                            fixes_failed.append("Failed to switch to T-Mobile 5G")
                    elif current_band == "5 GHz":
                        result = bash_cmd.connect_tmobile_2g()
                        fixes_attempted.append("Switch to T-Mobile 2.4GHz")
                        if "connected" in result.lower():
                            fixes_successful.append("Switched to T-Mobile 2.4GHz")
                        else:
                            fixes_failed.append("Failed to switch to T-Mobile 2.4GHz")
                except Exception as e:
                    fixes_failed.append(f"Band switching error: {e}")
            
            # General network issues
            if any(word in question_lower for word in ['problem', 'issue', 'trouble', 'help', 'fix']):
                logger.info("🔧 Attempting general network fixes...")
                
                # Try reloading network modules
                try:
                    result = bash_cmd.reload_network_modules()
                    fixes_attempted.append("Reload network modules")
                    if "reloaded" in result.lower():
                        fixes_successful.append("Network modules reloaded")
                    else:
                        fixes_failed.append("Network module reload failed")
                except Exception as e:
                    fixes_failed.append(f"Network module reload error: {e}")
            
            return {
                "fixes_attempted": fixes_attempted,
                "fixes_successful": fixes_successful,
                "fixes_failed": fixes_failed,
                "total_attempted": len(fixes_attempted),
                "total_successful": len(fixes_successful),
                "total_failed": len(fixes_failed)
            }
            
        except Exception as e:
            logger.error(f"Error in automatic fix attempt: {e}")
            return {
                "fixes_attempted": [],
                "fixes_successful": [],
                "fixes_failed": [f"Automatic fix system error: {e}"],
                "total_attempted": 0,
                "total_successful": 0,
                "total_failed": 1
            }
    
    def chat(self, message: str) -> Dict[str, Any]:
        """Main chat function with RAG + AI model"""
        logger.info(f"User question: {message}")
        
        # Get network data with smart collection based on question
        network_data = self.get_network_data(message)
        
        # Attempt automatic fixes for troubleshooting questions
        fix_results = None
        question_lower = message.lower()
        if any(word in question_lower for word in ['problem', 'issue', 'wrong', 'slow', 'bad', 'troubleshoot', 'help', 'fix', 'improve', 'optimize', 'signal', 'weak', 'poor', 'connection']):
            logger.info("🔧 Attempting automatic fixes...")
            fix_results = self.attempt_automatic_fix(message, network_data)
            network_data['automatic_fixes'] = fix_results
        
        # Generate AI response using RAG + model
        response = self.generate_ai_response(message, network_data)
        
        return {
            "response": response,
            "timestamp": time.time(),
            "network_data": network_data,
            "request_id": f"req_{int(time.time() * 1000)}",
            "ai_model_used": self.model is not None,
            "rag_enabled": self.vectorizer is not None,
            "automatic_fixes_attempted": fix_results is not None,
            "fixes_successful": fix_results['total_successful'] if fix_results else 0,
            "fixes_failed": fix_results['total_failed'] if fix_results else 0
        }
    
    def get_detailed_wifi_analysis(self) -> Dict[str, Any]:
        """Get detailed WiFi analysis for signal-related questions"""
        try:
            analysis = {
                "available_networks": [],
                "signal_quality": "unknown",
                "interference_sources": [],
                "recommendations": []
            }
            
            system = platform.system()
            
            if system == "Darwin":  # macOS
                # Get available networks
                try:
                    result = subprocess.run(['networksetup', '-listallhardwareports'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        analysis["network_interfaces"] = result.stdout
                except:
                    pass
                
                # Get WiFi scan (if available)
                try:
                    scan_result = subprocess.run(['system_profiler', 'SPAirPortDataType'], 
                                               capture_output=True, text=True, timeout=10)
                    if scan_result.returncode == 0:
                        analysis["wifi_details"] = scan_result.stdout
                except:
                    pass
            
            elif system == "Linux":
                # Get WiFi scan
                try:
                    scan_result = subprocess.run(['iwlist', 'scan'], 
                                               capture_output=True, text=True, timeout=10)
                    if scan_result.returncode == 0:
                        analysis["wifi_scan"] = scan_result.stdout
                except:
                    pass
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in detailed WiFi analysis: {e}")
            return {"error": str(e)}
    
    def get_speed_analysis(self) -> Dict[str, Any]:
        """Get speed analysis for performance-related questions"""
        try:
            analysis = {
                "speed_tests": {},
                "latency_tests": {},
                "bandwidth_utilization": "unknown"
            }
            
            # Multiple latency tests
            latency_targets = ["8.8.8.8", "1.1.1.1", "google.com"]
            for target in latency_targets:
                try:
                    result = subprocess.run(['ping', '-c', '3', target], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        latency_match = re.search(r'time=([0-9.]+)', result.stdout)
                        if latency_match:
                            analysis["latency_tests"][target] = f"{latency_match.group(1)}ms"
                except:
                    analysis["latency_tests"][target] = "timeout"
            
            # Get network interface speeds
            try:
                interfaces = psutil.net_if_stats()
                analysis["interface_speeds"] = {}
                for interface, stats in interfaces.items():
                    if stats.isup:
                        analysis["interface_speeds"][interface] = {
                            "speed": stats.speed,
                            "duplex": stats.duplex
                        }
            except:
                pass
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in speed analysis: {e}")
            return {"error": str(e)}
    
    def get_security_analysis(self) -> Dict[str, Any]:
        """Get security analysis for security-related questions"""
        try:
            analysis = {
                "dns_servers": [],
                "firewall_status": "unknown",
                "vpn_connections": [],
                "encryption_info": "unknown"
            }
            
            # Get DNS servers
            try:
                if platform.system() == "Darwin":
                    result = subprocess.run(['networksetup', '-getdnsservers', 'Wi-Fi'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        analysis["dns_servers"] = result.stdout.strip().split('\n')
                elif platform.system() == "Linux":
                    with open('/etc/resolv.conf', 'r') as f:
                        dns_content = f.read()
                        analysis["dns_servers"] = dns_content
            except:
                pass
            
            # Check for VPN connections
            try:
                connections = psutil.net_connections()
                vpn_connections = []
                for conn in connections:
                    if conn.status == 'ESTABLISHED' and conn.raddr:
                        # Simple heuristic for VPN detection
                        if any(port in [443, 1194, 1723, 500, 4500] for port in [conn.laddr.port, conn.raddr.port]):
                            vpn_connections.append(f"{conn.laddr.ip}:{conn.laddr.port} -> {conn.raddr.ip}:{conn.raddr.port}")
                analysis["vpn_connections"] = vpn_connections
            except:
                pass
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in security analysis: {e}")
            return {"error": str(e)}
    
    def get_network_diagnostics(self) -> Dict[str, Any]:
        """Get diagnostic data for problem-related questions"""
        try:
            diagnostics = {
                "network_interfaces": [],
                "routing_table": "unknown",
                "dns_resolution": {},
                "connectivity_tests": {}
            }
            
            # Get all network interfaces
            try:
                interfaces = psutil.net_if_addrs()
                for interface, addresses in interfaces.items():
                    interface_info = {"name": interface, "addresses": []}
                    for addr in addresses:
                        interface_info["addresses"].append({
                            "family": str(addr.family),
                            "address": addr.address,
                            "netmask": addr.netmask
                        })
                    diagnostics["network_interfaces"].append(interface_info)
            except:
                pass
            
            # Test DNS resolution
            dns_targets = ["google.com", "cloudflare.com", "github.com"]
            for target in dns_targets:
                try:
                    ip = socket.gethostbyname(target)
                    diagnostics["dns_resolution"][target] = ip
                except:
                    diagnostics["dns_resolution"][target] = "failed"
            
            # Connectivity tests
            test_urls = ["http://google.com", "https://google.com", "http://cloudflare.com"]
            for url in test_urls:
                try:
                    response = requests.get(url, timeout=5)
                    diagnostics["connectivity_tests"][url] = f"HTTP {response.status_code}"
                except Exception as e:
                    diagnostics["connectivity_tests"][url] = f"Error: {str(e)[:50]}"
            
            return diagnostics
            
        except Exception as e:
            logger.error(f"Error in network diagnostics: {e}")
            return {"error": str(e)}
    
    def get_comprehensive_analysis(self) -> Dict[str, Any]:
        """Get comprehensive analysis for detailed requests"""
        try:
            comprehensive = {
                "system_info": {},
                "network_topology": {},
                "performance_metrics": {},
                "security_audit": {}
            }
            
            # System information
            try:
                comprehensive["system_info"] = {
                    "platform": platform.system(),
                    "platform_version": platform.version(),
                    "architecture": platform.architecture(),
                    "hostname": socket.gethostname(),
                    "cpu_count": psutil.cpu_count(),
                    "memory_total": psutil.virtual_memory().total,
                    "boot_time": psutil.boot_time()
                }
            except:
                pass
            
            # Network topology
            try:
                comprehensive["network_topology"] = {
                    "all_interfaces": list(psutil.net_if_addrs().keys()),
                    "active_connections": len(psutil.net_connections()),
                    "network_io": dict(psutil.net_io_counters()._asdict())
                }
            except:
                pass
            
            # Performance metrics
            try:
                comprehensive["performance_metrics"] = {
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_io": dict(psutil.disk_io_counters()._asdict()) if psutil.disk_io_counters() else {},
                    "network_io": dict(psutil.net_io_counters()._asdict())
                }
            except:
                pass
            
            return comprehensive
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            return {"error": str(e)}

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

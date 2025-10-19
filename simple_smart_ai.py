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
from network_diagnostics import get_diagnostics

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleSmartAI:
    def __init__(self, test_mode=False):
        self.tokenizer = None
        self.model = None
        self.vectorizer = None
        self.knowledge_base = []
        self.embeddings = None
        self.test_mode = test_mode  # Enable test mode to simulate problems
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
        """Load WiFi knowledge base with comprehensive network quality standards and benchmarks"""
        return [
            {
                "title": "WiFi Signal Strength Standards",
                "content": "Excellent signal: -30 to -50 dBm (strong connection, full speed). Good signal: -50 to -60 dBm (reliable connection, good speed). Fair signal: -60 to -70 dBm (usable but may be slow). Poor signal: -70 to -80 dBm (unstable connection, frequent drops). Very poor signal: below -80 dBm (connection problems expected).",
                "category": "signal_quality",
                "keywords": ["signal strength", "dBm", "excellent", "good", "fair", "poor", "connection quality", "bars", "weak", "strong"]
            },
            {
                "title": "Internet Speed and Latency Benchmarks",
                "content": "Excellent latency: 0-20ms (gaming, video calls, real-time apps). Good latency: 20-50ms (streaming, browsing, most apps). Fair latency: 50-100ms (basic web use, some delays). Poor latency: 100-200ms (noticeable delays, slow loading). Very poor latency: above 200ms (significant problems, timeouts). Speed requirements: 1-5 Mbps (basic), 5-25 Mbps (HD streaming), 25-100 Mbps (4K streaming), 100+ Mbps (multiple devices).",
                "category": "speed_latency",
                "keywords": ["latency", "ping", "ms", "speed", "Mbps", "bandwidth", "fast", "slow", "excellent", "good", "fair", "poor", "response time", "loading"]
            },
            {
                "title": "Network Connection Quality Indicators",
                "content": "A healthy network connection shows: WiFi status 'connected', internet connectivity working, DNS resolution successful, latency under 100ms, signal strength above -70 dBm, stable connection. Red flags include: disconnected status, failed internet tests, DNS errors, latency over 200ms, signal below -80 dBm, frequent disconnections.",
                "category": "connection_health",
                "keywords": ["connection status", "health indicators", "red flags", "network quality", "diagnostics", "working", "not working", "connected", "disconnected"]
            },
            {
                "title": "WiFi Network Performance Standards",
                "content": "WiFi 6 (802.11ax): Latest standard with best performance, handles many devices. WiFi 5 (802.11ac): Good performance, widely supported. WiFi 4 (802.11n): Older but functional. 5GHz band: Faster speeds, shorter range, less interference. 2.4GHz band: Slower speeds, longer range, more interference. Channel width affects speed: 20MHz (basic), 40MHz (better), 80MHz (fast), 160MHz (fastest).",
                "category": "network_standards",
                "keywords": ["WiFi standards", "802.11", "frequency bands", "channel width", "performance", "compatibility", "5GHz", "2.4GHz", "WiFi 6", "WiFi 5"]
            },
            {
                "title": "Internet Speed Requirements by Activity",
                "content": "Basic browsing: 1-5 Mbps. Email and social media: 1-3 Mbps. HD video streaming: 5-25 Mbps. 4K video streaming: 25-100 Mbps. Online gaming: 3-6 Mbps. Video conferencing: 1-4 Mbps. Multiple devices: 25-100+ Mbps depending on usage. Upload speeds typically 10-20% of download speeds. Speed tests measure actual throughput vs. advertised speeds.",
                "category": "speed_requirements",
                "keywords": ["bandwidth", "Mbps", "streaming", "gaming", "video conferencing", "multiple devices", "upload", "download", "speed test", "throughput", "advertised speed"]
            },
            {
                "title": "Network Stability and Reliability Indicators",
                "content": "Stable connection shows: Consistent signal strength, low packet loss (under 1%), stable latency, no frequent disconnections, reliable DNS resolution, consistent speeds. Unstable signs: Fluctuating signal, high packet loss, latency spikes, frequent drops, DNS failures, inconsistent speeds, intermittent connectivity.",
                "category": "stability_metrics",
                "keywords": ["stability", "packet loss", "disconnections", "fluctuations", "reliability", "consistency", "intermittent", "unstable", "stable", "drops", "spikes"]
            },
            {
                "title": "WiFi Security and Authentication Standards",
                "content": "WPA3: Latest and most secure encryption, best for new devices. WPA2: Widely used, secure for most purposes, compatible with most devices. WPA: Older, less secure, legacy support. WEP: Deprecated, insecure, should be avoided. Open networks: No encryption, not recommended for sensitive data. Strong passwords: 12+ characters, mixed case, numbers, symbols.",
                "category": "security_standards",
                "keywords": ["WPA3", "WPA2", "encryption", "security", "authentication", "passwords", "standards", "encryption", "secure", "insecure", "open network"]
            },
            {
                "title": "Network Troubleshooting Quality Indicators",
                "content": "Good network health: Connected status, working internet, fast DNS resolution, low latency (under 50ms), strong signal (above -60 dBm), stable connection, no packet loss. Problem indicators: Disconnected status, no internet access, DNS failures, high latency (over 100ms), weak signal (below -70 dBm), frequent disconnections, packet loss, slow speeds.",
                "category": "troubleshooting_indicators",
                "keywords": ["troubleshooting", "problem indicators", "good health", "bad health", "issues", "problems", "symptoms", "diagnostics", "network health"]
            },
            {
                "title": "WiFi Range and Coverage Standards",
                "content": "Excellent coverage: Signal strength -30 to -50 dBm throughout area. Good coverage: Signal strength -50 to -60 dBm in most areas. Fair coverage: Signal strength -60 to -70 dBm, some dead spots. Poor coverage: Signal strength -70 to -80 dBm, many dead spots. Very poor coverage: Signal below -80 dBm, frequent dead spots. Factors affecting range: Router placement, obstacles, interference, building materials, antenna orientation.",
                "category": "coverage_standards",
                "keywords": ["coverage", "range", "dead spots", "signal strength", "dBm", "router placement", "obstacles", "interference", "building materials", "antenna"]
            },
            {
                "title": "Network Performance Optimization Standards",
                "content": "Optimal performance: Latest WiFi standard (WiFi 6), 5GHz band, wide channels (80-160MHz), strong signal (-50 dBm or better), low latency (under 20ms), no interference, proper router placement. Performance issues: Old WiFi standard, 2.4GHz band, narrow channels, weak signal, high latency, interference, poor placement, too many devices, outdated equipment.",
                "category": "optimization_standards",
                "keywords": ["optimization", "performance", "optimal", "issues", "WiFi standard", "frequency band", "channels", "signal strength", "latency", "interference", "placement", "devices", "equipment"]
            },
            {
                "title": "External Device Connectivity (Printers, Phones, IoT)",
                "content": "External devices like printers, mobile phones, smart home devices, and IoT gadgets cannot be automatically fixed by network diagnostics. Suggestions for external device issues: 1) Ensure device WiFi is enabled and searching for networks. 2) Verify device is within router range (signal strength). 3) Check if device supports your WiFi frequency (2.4GHz vs 5GHz). 4) Restart the device. 5) Forget and reconnect to the network on the device. 6) Check device-specific settings (firewall, MAC filtering). 7) Verify router allows new devices (not at device limit). 8) Update device firmware/drivers. This system can only provide guidance, not direct control of external devices.",
                "category": "external_devices",
                "keywords": ["printer", "phone", "mobile", "device", "iot", "smart home", "connect device", "external", "cannot connect", "won't connect", "device won't", "printer won't"]
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
        """Generate AI response using diagnostics + automatic fixes + suggestions"""
        # Check if question requires live diagnostics
        question_lower = user_question.lower()
        needs_diagnostics = any(keyword in question_lower for keyword in [
            'how', 'status', 'speed', 'fast', 'slow', 'check', 'test',
            'wifi', 'internet', 'connection', 'quality', 'working', 'signal',
            'weak', 'poor', 'latency', 'ping'
        ])

        # Step 1: Run diagnostics if needed
        diagnostic_results = None
        if needs_diagnostics:
            logger.info("🔧 Collecting diagnostic data...")
            diagnostics = get_diagnostics()
            # Enable verbose mode to show progress in console
            diagnostic_results = diagnostics.analyze_wifi_quality(network_data, verbose=True)
            logger.info(f"✅ Diagnostics complete: {diagnostic_results.get('overall_status')}")

        # Step 2: Attempt automatic fixes if problems detected OR if band switching requested
        fix_results = None
        question_lower = user_question.lower()
        band_switch_requested = any(phrase in question_lower for phrase in ['fastest band', 'faster band', 'best band', 'switch band', 'better band', 'optimize band'])

        if (diagnostic_results and diagnostic_results.get('issues')) or band_switch_requested:
            logger.info("🔧 Attempting automatic fixes...")
            fix_results = self.attempt_automatic_fix(user_question, network_data)
            logger.info(f"✅ Fix attempts complete: {len(fix_results.get('fixes_successful', []))} successful")

        # Get relevant knowledge for RAG
        relevant_knowledge = self.retrieve_relevant_knowledge(user_question, network_data)

        # Step 3: Generate response with diagnostic data + fix results
        if self.model and self.tokenizer:
            return self._generate_ai_text(user_question, network_data, relevant_knowledge, diagnostic_results, fix_results)
        else:
            return self._generate_rule_based_response(user_question, network_data, relevant_knowledge, diagnostic_results, fix_results)
    
    def _generate_ai_text(self, user_question: str, network_data: Dict[str, Any], relevant_knowledge: List[Dict[str, Any]], diagnostic_results: Dict[str, Any] = None, fix_results: Dict[str, Any] = None) -> str:
        """Generate conversational AI response using the loaded model with diagnostic data and fix results"""
        try:
            # Get the fallback response first
            fallback_response = self._generate_rule_based_response(user_question, network_data, relevant_knowledge, diagnostic_results, fix_results)

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

    def _format_response_with_fixes(self, base_response: str, fix_results: Dict[str, Any] = None) -> str:
        """Format response with automatic fix results prepended"""
        if not fix_results:
            return base_response

        response_parts = []
        fixes_successful = fix_results.get('fixes_successful', [])
        fixes_failed = fix_results.get('fixes_failed', [])

        if fixes_successful:
            response_parts.append("🔧 **Automatic Fixes Applied:**")
            for fix in fixes_successful:
                response_parts.append(f"  ✅ {fix}")
            response_parts.append("")

        if fixes_failed:
            response_parts.append("⚠️ **Some fixes couldn't be applied:**")
            for fix in fixes_failed:
                response_parts.append(f"  ❌ {fix}")
            response_parts.append("")

        response_parts.append(base_response)
        return "\n".join(response_parts)

    def _generate_rule_based_response(self, user_question: str, network_data: Dict[str, Any], relevant_knowledge: List[Dict[str, Any]], diagnostic_results: Dict[str, Any] = None, fix_results: Dict[str, Any] = None) -> str:
        """Generate conversational rule-based response with diagnostics and fix results"""
        wifi = network_data.get('wifi', {})
        connectivity = network_data.get('connectivity', {})
        performance = network_data.get('performance', {})

        # Analyze the question and network state to give appropriate response
        question_lower = user_question.lower()
        
        # Get actual network status for intelligent decision making
        is_wifi_connected = wifi.get('status') == 'connected'
        is_internet_working = connectivity.get('internet_connected', False)
        signal_strength = wifi.get('signal_strength', 'unknown')
        latency = connectivity.get('latency', 'unknown')
        
        # Determine if there are actual network problems based on real data
        has_actual_problems = self._detect_actual_network_problems(network_data)
        
        logger.info(f"🔍 Network Analysis: WiFi={is_wifi_connected}, Internet={is_internet_working}, Problems={has_actual_problems}")
        
        # If user claims problems but network is actually working well, provide reassurance
        if any(word in question_lower for word in ['not connected', 'disconnected', 'no internet', 'cant connect', 'wont connect', 'cant browse', 'no signal', 'offline']) and is_wifi_connected and is_internet_working:
            return self._provide_reassurance_response(network_data)
        
        # If user claims slow internet but speed is actually good
        if any(word in question_lower for word in ['slow', 'sluggish', 'crawling', 'terrible speed', 'awful speed']) and is_internet_working and self._is_speed_good(latency):
            return self._provide_speed_reassurance_response(network_data)
        
        # If user claims weak signal but signal is actually good
        if any(word in question_lower for word in ['weak signal', 'poor signal', 'bad signal', 'low bars', 'terrible signal']) and is_wifi_connected and self._is_signal_good(signal_strength):
            return self._provide_signal_reassurance_response(network_data)
        
        # If asking about problems and there ARE CRITICAL CLI-detected problems, provide help
        if any(word in question_lower for word in ['problem', 'issue', 'wrong', 'slow', 'bad', 'troubleshoot', 'help', 'fix', 'improve', 'optimize', 'signal', 'weak', 'poor', 'connection']) and has_actual_problems:
            logger.info("🔧 CLI detected CRITICAL network problems, attempting targeted fix...")
            # First tell user what's wrong, then attempt fix
            problem_description = self._describe_network_problems(network_data)
            fix_result = self._attempt_targeted_fix(user_question, network_data)
            return f"{problem_description}\n\n{fix_result}"
        
        # If asking about problems but network is actually working fine, provide reassurance
        elif any(word in question_lower for word in ['problem', 'issue', 'wrong', 'slow', 'bad', 'troubleshoot', 'help', 'fix', 'improve', 'optimize', 'signal', 'weak', 'poor', 'connection']) and not has_actual_problems:
            return self._provide_general_reassurance_response(network_data)

        # Specific handler for latency questions
        elif any(word in question_lower for word in ['latency', 'ping', 'lag', 'delay', 'response time']):
            if diagnostic_results:
                ping_test = diagnostic_results.get('ping_test', {})
                avg_latency = ping_test.get('avg_latency', 0)
                packet_loss = ping_test.get('packet_loss', 0)

                response_parts = []
                if fix_results:
                    response_parts.append(self._format_response_with_fixes("", fix_results).strip())

                response_parts.append(f"Your network latency is {avg_latency:.1f}ms with {packet_loss}% packet loss.")

                if avg_latency < 20:
                    response_parts.append("This is excellent for gaming and video calls.")
                elif avg_latency < 50:
                    response_parts.append("This is good for most activities.")
                elif avg_latency < 100:
                    response_parts.append("This may cause some delays in real-time applications.")
                else:
                    response_parts.append("This is high and may cause noticeable delays.")

                if relevant_knowledge:
                    response_parts.append(f"\n{relevant_knowledge[0]['content']}")

                return "\n".join(response_parts)
            else:
                return f"Your current latency is {latency}. Let me run diagnostics to get more details."

        # Specific handler for external device questions (printer, phone, etc.)
        elif any(word in question_lower for word in ['printer', 'phone', 'device', 'iot', 'smart home']):
            response_parts = []

            # Acknowledge the external device
            device_type = 'device'
            if 'printer' in question_lower:
                device_type = 'printer'
            elif 'phone' in question_lower:
                device_type = 'phone'

            response_parts.append(f"I cannot directly control your {device_type}, but here are troubleshooting suggestions:")

            # Add RAG knowledge if available
            if relevant_knowledge:
                for knowledge in relevant_knowledge[:1]:
                    if 'external' in knowledge.get('category', '').lower():
                        response_parts.append(f"\n{knowledge['content']}")

            # Show host network is working
            response_parts.append(f"\nYour network status: WiFi: {'Connected' if is_wifi_connected else 'Not Connected'}, Internet: {'Connected' if is_internet_working else 'Not Connected'}, Latency: {latency}")

            return "\n".join(response_parts)

        # Specific handler for band switching questions (Demo 5)
        elif any(phrase in question_lower for phrase in ['fastest band', 'faster band', 'best band', 'switch band', 'better band', 'optimize band']):
            response_parts = []

            if fix_results and fix_results.get('fixes_successful'):
                # Extract band switching results from fix_results
                band_switch_message = None
                for fix in fix_results['fixes_successful']:
                    if 'band' in fix.lower() and ('switched' in fix.lower() or 'stayed' in fix.lower()):
                        band_switch_message = fix
                        break

                if band_switch_message:
                    response_parts.append("⚡ **WiFi Band Optimization Complete!**\n")

                    # Parse the speeds from the message (e.g., "Switched to faster 5 GHz band (87.3 Mbps vs 42.1 Mbps)")
                    if '(' in band_switch_message and 'Mbps vs' in band_switch_message:
                        # Extract speeds
                        speed_part = band_switch_message[band_switch_message.find('(')+1:band_switch_message.find(')')]
                        speeds = speed_part.split(' vs ')
                        new_speed = speeds[0].replace(' Mbps', '')
                        old_speed = speeds[1].replace(' Mbps', '')

                        if 'switched to faster' in band_switch_message.lower():
                            improvement = float(new_speed) - float(old_speed)
                            improvement_pct = (improvement / float(old_speed)) * 100
                            response_parts.append(f"**Results:**")
                            response_parts.append(f"• Previous speed: {old_speed} Mbps")
                            response_parts.append(f"• New speed: {new_speed} Mbps")
                            response_parts.append(f"• **Speed increase: +{improvement:.1f} Mbps ({improvement_pct:.0f}% faster!)**\n")
                            response_parts.append("✅ You're now connected to the faster band for optimal performance!")
                        else:
                            response_parts.append(f"**Results:**")
                            response_parts.append(f"• Current speed: {new_speed} Mbps")
                            response_parts.append(f"• Tested other band: {old_speed} Mbps\n")
                            response_parts.append("✅ You were already on the fastest available band!")
                    else:
                        response_parts.append(f"✅ {band_switch_message}")

                        if 'switched to faster' in band_switch_message.lower():
                            response_parts.append("\nYou're now connected to the faster band for optimal performance!")
                        else:
                            response_parts.append("\nYou were already on the fastest available band!")
                else:
                    response_parts.append("I tested both WiFi bands and optimized your connection.")
            elif fix_results and fix_results.get('fixes_failed'):
                # Band switching failed
                error_message = None
                for fix in fix_results['fixes_failed']:
                    if 'band' in fix.lower():
                        error_message = fix
                        break

                if error_message:
                    response_parts.append("⚠️ **Band Optimization Failed**\n")
                    response_parts.append(f"Error: {error_message}")
                    response_parts.append("\n**Note:** Band switching requires:")
                    response_parts.append("• Running on actual hardware (Raspberry Pi)")
                    response_parts.append("• NetworkManager (nmcli) installed")
                    response_parts.append("• Connection to T-Mobile or T-Mobile 5G networks")
                else:
                    response_parts.append("⚠️ Unable to test bands at this time.")
            else:
                # No fix results, just provide status
                current_band = bash_cmd.identify_band()
                response_parts.append(f"📊 You're currently on the {current_band} band.")
                response_parts.append("\nI can test both bands and switch you to the fastest one. This will take about 30-60 seconds.")

            return "\n".join(response_parts)

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
                    
                    return f"Your WiFi is connected to **{ssid}** with {emoji} **{quality}** signal strength ({signal} dBm)."
                except:
                    return f"Your WiFi is connected to **{ssid}**!"
            else:
                return f"Your WiFi is connected to **{ssid}**!"
        
        # If asking about internet and it's connected
        elif any(word in question_lower for word in ['internet', 'online', 'web', 'browse']) and connectivity.get('internet_connected'):
            latency = connectivity.get('latency', 'unknown')
            if latency != 'unknown':
                return f"Your connection speed is {latency}."
            else:
                return "Your internet connection is unknown."
        
        
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
        
        # Check if input has nothing to do with networks
        network_keywords = ['wifi', 'internet', 'network', 'connection', 'signal', 'speed', 'latency', 'bandwidth', 'router', 'modem', 'ethernet', 'wireless', 'online', 'offline', 'connect', 'disconnect', 'browse', 'web', 'ping', 'dns', 'ip', 'troubleshoot', 'fix', 'problem', 'issue', 'slow', 'fast', 'weak', 'strong', 'quality', 'performance', 'printer', 'device', 'phone', 'lag', 'delay', 'high', 'low', 'band', 'optimize']

        has_network_keywords = any(keyword in question_lower for keyword in network_keywords)

        if not has_network_keywords:
            return "🤔 I don't recognize that input. I'm a network assistant - please try asking about WiFi, internet, or network issues like 'My WiFi is slow' or 'I can't connect to the internet'."

        # If we have network keywords but didn't match earlier conditions, provide general network status
        base_response = self._analyze_current_network(network_data)
        return self._format_response_with_fixes(base_response, fix_results)
    
    def _attempt_targeted_fix(self, user_question: str, network_data: Dict[str, Any]) -> str:
        """Simplified flow: detect specific problem → attempt targeted fix → report result"""
        question_lower = user_question.lower()
        
        # Determine the specific problem type based on user's question keywords first
        if any(word in question_lower for word in ['latency', 'ping', 'responsive', 'delay', 'lag']):
            return self._fix_latency_issue(user_question, network_data)
        
        elif any(word in question_lower for word in ['bandwidth', 'throughput', 'capacity', 'data rate']):
            return self._fix_bandwidth_issue(user_question, network_data)
        
        elif any(word in question_lower for word in ['signal', 'strength', 'interference', 'quality', 'bars']):
            return self._fix_signal_integrity_issue(user_question, network_data)
        
        elif any(word in question_lower for word in ['slow', 'speed', 'performance', 'fast']):
            return self._fix_speed_issue(user_question, network_data)
        
        elif any(word in question_lower for word in ['wifi', 'wireless', 'connection', 'disconnected']):
            return self._fix_wifi_issue(user_question, network_data)
        
        elif any(word in question_lower for word in ['internet', 'web', 'browse', 'online']):
            return self._fix_internet_issue(user_question, network_data)
        
        else:
            return self._fix_general_network_issue(user_question, network_data)
    
    def _fix_internet_issue(self, user_question: str, network_data: Dict[str, Any]) -> str:
        """Fix internet connectivity issues"""
        logger.info("🌐 Attempting to fix internet issues...")
        
        # Try DNS-related fixes first
        try:
            result = bash_cmd.flush_dns_cache()
            if "flushed" in result.lower():
                return "✅ Fixed! I flushed your DNS cache. Try browsing the web now."
        except:
            pass
        
        try:
            result = bash_cmd.restart_dns_service()
            if "restarted" in result.lower():
                return "✅ Fixed! I restarted your DNS service. Try browsing the web now."
        except:
            pass
        
        # Try IP renewal
        try:
            result = bash_cmd.release_renew_ip()
            if "released" in result.lower() and "renewed" in result.lower():
                return "✅ Fixed! I renewed your IP address. Try browsing the web now."
        except:
            pass
        
        # Try network restart
        try:
            result = bash_cmd.restart_network_stack()
            if "restarted" in result.lower():
                return "✅ Fixed! I restarted your network stack. Try browsing the web now."
        except:
            pass
        
        # If fixes failed, give suggestion
        return "❌ I couldn't fix the internet issue automatically. Try: 1) Restart your router, 2) Check if other devices work, 3) Contact your ISP if the problem persists."
    
    def _fix_wifi_issue(self, user_question: str, network_data: Dict[str, Any]) -> str:
        """Fix WiFi connectivity issues"""
        logger.info("📶 Attempting to fix WiFi issues...")
        
        # Try WiFi adapter reset first
        try:
            result = bash_cmd.reset_wifi_adapter()
            if "reset" in result.lower():
                return "✅ Fixed! I reset your WiFi adapter. Try reconnecting to your network now."
        except:
            pass
        
        # Try reloading WiFi modules
        try:
            result = bash_cmd.reload_network_modules()
            if "reloaded" in result.lower():
                return "✅ Fixed! I reloaded your WiFi modules. Try reconnecting to WiFi now."
        except:
            pass
        
        # Try network manager restart
        try:
            result = bash_cmd.reset_networkmanager()
            if "restarted" in result.lower():
                return "✅ Fixed! I restarted your network manager. Try reconnecting to WiFi now."
        except:
            pass
        
        # Try full network restart
        try:
            result = bash_cmd.restart_network_stack()
            if "restarted" in result.lower():
                return "✅ Fixed! I restarted your network stack. Try reconnecting to WiFi now."
        except:
            pass
        
        # If fixes failed, give suggestion
        return "❌ I couldn't fix the WiFi issue automatically. Try: 1) Move closer to your router, 2) Restart your router, 3) Check if other devices can connect."
    
    def _fix_speed_issue(self, user_question: str, network_data: Dict[str, Any]) -> str:
        """Fix network speed/performance issues"""
        logger.info("⚡ Attempting to fix speed issues...")
        
        # Try changing WiFi band for better performance
        try:
            result = bash_cmd.change_band()
            if "connected" in result.lower():
                return "✅ Fixed! I switched you to a faster WiFi band. Your internet should be faster now."
        except:
            pass
        
        # Try DNS flush for faster resolution
        try:
            result = bash_cmd.flush_dns_cache()
            if "flushed" in result.lower():
                return "✅ Fixed! I flushed your DNS cache. Your internet should be faster now."
        except:
            pass
        
        # Try IP renewal for fresh connection
        try:
            result = bash_cmd.release_renew_ip()
            if "released" in result.lower() and "renewed" in result.lower():
                return "✅ Fixed! I renewed your IP address. Your internet should be faster now."
        except:
            pass
        
        # Try network restart
        try:
            result = bash_cmd.restart_network_stack()
            if "restarted" in result.lower():
                return "✅ Fixed! I restarted your network stack. Your internet should be faster now."
        except:
            pass
        
        # If fixes failed, give suggestion
        return "❌ I couldn't fix the speed issue automatically. Try: 1) Move closer to your router, 2) Close other apps using internet, 3) Restart your router, 4) Check if other devices are slow too."
    
    def _fix_general_network_issue(self, user_question: str, network_data: Dict[str, Any]) -> str:
        """Fix general network issues"""
        logger.info("🔧 Attempting to fix general network issues...")
        
        # Try comprehensive network reset
        try:
            result = bash_cmd.restart_network_stack()
            if "restarted" in result.lower():
                return "✅ Fixed! I restarted your network stack. Try using your network now."
        except:
            pass
        
        # Try reloading network modules
        try:
            result = bash_cmd.reload_network_modules()
            if "reloaded" in result.lower():
                return "✅ Fixed! I reloaded your network modules. Try using your network now."
        except:
            pass
        
        # Try IP renewal
        try:
            result = bash_cmd.release_renew_ip()
            if "released" in result.lower() and "renewed" in result.lower():
                return "✅ Fixed! I renewed your IP address. Try using your network now."
        except:
            pass
        
        # Try DNS flush
        try:
            result = bash_cmd.flush_dns_cache()
            if "flushed" in result.lower():
                return "✅ Fixed! I flushed your DNS cache. Try using your network now."
        except:
            pass
        
        # If fixes failed, give suggestion
        return "❌ I couldn't fix the network issue automatically. Try: 1) Restart your router, 2) Restart your device, 3) Check if other devices work, 4) Contact your ISP if the problem persists."
    
    def _fix_latency_issue(self, user_question: str, network_data: Dict[str, Any]) -> str:
        """Fix latency and responsiveness issues"""
        logger.info("⏱️ Attempting to fix latency issues...")
        
        # Try latency-specific fixes
        try:
            result = bash_cmd.fix_latency_issues()
            if "addressed" in result.lower():
                return "✅ Fixed! I optimized your network stack for better latency. Try your connection now."
        except:
            pass
        
        # Try DNS optimization
        try:
            result = bash_cmd.flush_dns_cache()
            if "flushed" in result.lower():
                return "✅ Fixed! I flushed your DNS cache for faster resolution. Try your connection now."
        except:
            pass
        
        # Try network performance optimization
        try:
            result = bash_cmd.optimize_network_performance()
            if "optimized" in result.lower():
                return "✅ Fixed! I optimized your network performance settings. Try your connection now."
        except:
            pass
        
        # If fixes failed, give suggestion
        return "❌ I couldn't fix the latency issue automatically. Try: 1) Move closer to your router, 2) Close other apps, 3) Use a wired connection, 4) Check if other devices have the same issue."
    
    def _fix_bandwidth_issue(self, user_question: str, network_data: Dict[str, Any]) -> str:
        """Fix bandwidth and throughput issues"""
        logger.info("📊 Attempting to fix bandwidth issues...")
        
        # Try bandwidth optimization
        try:
            result = bash_cmd.optimize_bandwidth()
            if "optimized" in result.lower():
                return "✅ Fixed! I optimized your bandwidth settings. Try your connection now."
        except:
            pass
        
        # Try changing WiFi band for better performance
        try:
            result = bash_cmd.change_band()
            if "connected" in result.lower():
                return "✅ Fixed! I switched you to a faster WiFi band. Try your connection now."
        except:
            pass
        
        # Try network performance optimization
        try:
            result = bash_cmd.optimize_network_performance()
            if "optimized" in result.lower():
                return "✅ Fixed! I optimized your network performance. Try your connection now."
        except:
            pass
        
        # If fixes failed, give suggestion
        return "❌ I couldn't fix the bandwidth issue automatically. Try: 1) Move closer to your router, 2) Close other apps using internet, 3) Use 5GHz WiFi, 4) Check if other devices are using bandwidth."
    
    def _fix_signal_integrity_issue(self, user_question: str, network_data: Dict[str, Any]) -> str:
        """Handle poor WiFi signal - can't fix physically, provide helpful guidance"""
        logger.info("📶 Poor WiFi signal detected - providing guidance...")
        
        # Get current signal strength for context
        wifi = network_data.get('wifi', {})
        signal_strength = wifi.get('signal_strength', 'unknown')
        
        if signal_strength != 'unknown':
            try:
                signal_int = int(signal_strength.replace(' dBm', ''))
                if signal_int < -60:
                    return f"""🔴 **Poor WiFi Signal Detected** ({signal_strength})

**This is a physical issue that can't be fixed with software commands.**

**📍 Immediate Solutions:**
• **Move closer to your router** - This is the most effective fix
• **Remove obstacles** between you and the router (walls, furniture, appliances)
• **Check router placement** - Is it in a central location?
• **Try different rooms** to find better signal

**🔧 Advanced Solutions:**
• **WiFi extender** or **mesh network** for large spaces
• **Router upgrade** to newer WiFi 6/6E standard
• **Check for interference** from microwaves, Bluetooth devices, or other WiFi networks

**Current signal: {signal_strength}** (needs to be above -50 dBm for good performance)"""
            except:
                pass
        
        # Fallback if we can't parse signal strength
        return """🔴 **Poor WiFi Signal Detected**

**This is a physical issue that can't be fixed with software commands.**

**📍 Immediate Solutions:**
• **Move closer to your router** - This is the most effective fix
• **Remove obstacles** between you and the router
• **Check router placement** - Is it in a central location?

**🔧 Advanced Solutions:**
• **WiFi extender** or **mesh network** for large spaces
• **Router upgrade** to newer WiFi 6/6E standard"""
    
    def _detect_actual_network_problems(self, network_data: Dict[str, Any]) -> bool:
        """Detect if there are actual network problems based on real CLI data - only troubleshoot when there are definitive issues"""
        wifi = network_data.get('wifi', {})
        connectivity = network_data.get('connectivity', {})
        performance = network_data.get('performance', {})
        
        # Check for definitive problems that require troubleshooting
        problems = []
        
        # Only troubleshoot for CRITICAL issues detected by CLI commands
        # WiFi completely disconnected
        if wifi.get('status') != 'connected':
            problems.append("WiFi not connected")
            logger.info("🔍 CLI detected: WiFi is not connected")
        
        # Internet completely not working
        if not connectivity.get('internet_connected', False):
            problems.append("Internet not working")
            logger.info("🔍 CLI detected: Internet is not working")
        
        # Troubleshoot for poor signal (more sensitive detection)
        signal_strength = wifi.get('signal_strength', 'unknown')
        if signal_strength != 'unknown':
            try:
                # Extract numeric value from signal string like "-65 dBm"
                signal_int = int(signal_strength.replace(' dBm', ''))
                logger.info(f"🔍 Signal check: {signal_int} dBm, threshold: -60")
                if signal_int < -60:  # Poor signal threshold (more sensitive than -85)
                    problems.append("Poor WiFi signal")
                    logger.info(f"🔍 CLI detected: Poor WiFi signal ({signal_int} dBm)")
            except:
                pass
        
        # Only troubleshoot for EXTREMELY slow internet (not just "slow")
        latency = connectivity.get('latency', 'unknown')
        if latency != 'unknown':
            try:
                # Extract numeric value from latency string like "5.596ms"
                latency_num = float(latency.replace('ms', ''))
                if latency_num > 200:  # Only very high latency (more strict than 100ms)
                    problems.append("Extremely slow internet")
                    logger.info(f"🔍 CLI detected: Extremely slow internet ({latency_num}ms)")
            except:
                pass
        
        # Only troubleshoot if there are CRITICAL problems
        has_critical_problems = len(problems) > 0
        logger.info(f"🔍 CLI-based problem detection: {problems} -> Has critical problems: {has_critical_problems}")
        return has_critical_problems
    
    def _is_speed_good(self, latency: str) -> bool:
        """Check if internet speed is good based on latency"""
        if latency == 'unknown':
            return True  # Assume good if we can't measure
        
        try:
            latency_num = float(latency.replace('ms', ''))
            return latency_num < 50  # Good if under 50ms
        except:
            return True  # Assume good if we can't parse
    
    def _is_signal_good(self, signal_strength: str) -> bool:
        """Check if WiFi signal is good"""
        if signal_strength == 'unknown':
            return True  # Assume good if we can't measure
        
        try:
            signal_int = int(signal_strength)
            return signal_int > -50  # Good if better than -50 dBm (strict threshold for reassurance)
        except:
            return True  # Assume good if we can't parse
    
    def _provide_reassurance_response(self, network_data: Dict[str, Any]) -> str:
        """Provide reassurance when user thinks they're disconnected but they're actually connected"""
        wifi = network_data.get('wifi', {})
        connectivity = network_data.get('connectivity', {})
        ssid = wifi.get('ssid', 'your network')
        
        return f"✅ Actually, your network is working perfectly! You're connected to **{ssid}** and your internet is working well. Sometimes it takes a moment for websites to load, but your connection is solid!"
    
    def _provide_speed_reassurance_response(self, network_data: Dict[str, Any]) -> str:
        """Provide reassurance when user thinks internet is slow but it's actually good"""
        connectivity = network_data.get('connectivity', {})
        latency = connectivity.get('latency', 'unknown')
        
        if latency != 'unknown':
            return f"✅ Your internet speed is actually quite good! Your connection latency is {latency}, which is excellent for browsing and streaming. Sometimes websites can be slow due to their servers, but your connection is fast!"
        else:
            return "✅ Your internet connection is working well! Sometimes websites can be slow due to their servers, but your connection is solid!"
    
    def _provide_signal_reassurance_response(self, network_data: Dict[str, Any]) -> str:
        """Provide reassurance when user thinks signal is weak but it's actually good"""
        wifi = network_data.get('wifi', {})
        signal_strength = wifi.get('signal_strength', 'unknown')
        ssid = wifi.get('ssid', 'your network')
        
        if signal_strength != 'unknown':
            try:
                signal_int = int(signal_strength)
                if signal_int > -50:
                    quality = "excellent"
                    emoji = "🟢"
                elif signal_int > -70:
                    quality = "good"
                    emoji = "🟡"
                else:
                    quality = "fair"
                    emoji = "🟠"
                
                return f"✅ Your WiFi signal is actually {emoji} **{quality}**! You're connected to **{ssid}** with {signal_strength} dBm, which is a strong signal. Your connection should work great!"
            except:
                return f"✅ Your WiFi signal is strong! You're connected to **{ssid}** and your connection is working well."
        else:
            return f"✅ Your WiFi signal is good! You're connected to **{ssid}** and your connection is working well."
    
    def _provide_general_reassurance_response(self, network_data: Dict[str, Any]) -> str:
        """Provide general reassurance when user thinks there are problems but network is working fine"""
        wifi = network_data.get('wifi', {})
        connectivity = network_data.get('connectivity', {})
        ssid = wifi.get('ssid', 'your network')
        
        return f"✅ Actually, your network looks great! Your WiFi is connected to **{ssid}** and your internet is working well. Are you experiencing any specific issues? Sometimes restarting your browser or clearing its cache can help if websites seem slow."
    
    def _describe_network_problems(self, network_data: Dict[str, Any]) -> str:
        """Clearly describe what network problems were detected"""
        wifi = network_data.get('wifi', {})
        connectivity = network_data.get('connectivity', {})
        performance = network_data.get('performance', {})
        
        problems = []
        
        # WiFi issues
        if wifi.get('status') != 'connected':
            problems.append("🔴 **WiFi is disconnected** - You're not connected to any network")
        elif wifi.get('ssid') == 'None':
            problems.append("🔴 **WiFi connection lost** - No active network connection")
        
        # Internet issues  
        if not connectivity.get('internet_connected', False):
            problems.append("🔴 **Internet is down** - No internet connectivity detected")
        elif not connectivity.get('dns_working', False):
            problems.append("🔴 **DNS not working** - Can't resolve website addresses")
        
        # Signal issues
        signal_strength = wifi.get('signal_strength', 'unknown')
        if signal_strength != 'unknown':
            try:
                # Extract numeric value from signal string like "-65 dBm"
                signal_int = int(signal_strength.replace(' dBm', ''))
                if signal_int < -60:
                    problems.append(f"🔴 **Poor WiFi signal** - {signal_strength} (below -60 dBm threshold)")
                elif signal_int < -50:
                    problems.append(f"🟡 **Fair WiFi signal** - {signal_strength} (could be better)")
            except:
                pass
        
        # Speed issues
        latency = connectivity.get('latency', 'unknown')
        if latency != 'unknown':
            try:
                latency_num = float(latency.replace('ms', ''))
                if latency_num > 200:
                    problems.append(f"🔴 **Extremely slow internet** - {latency} latency (very poor)")
                elif latency_num > 100:
                    problems.append(f"🟡 **Slow internet** - {latency} latency (poor)")
            except:
                pass
        
        if problems:
            return "🚨 **I detected the following network problems:**\n\n" + "\n".join(problems)
        else:
            return "🔍 **I'm analyzing your network issues...**"
    
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

        base_response = "\n".join(analysis_parts)
        return self._format_response_with_fixes(base_response, fix_results)
    
    def get_network_data(self, user_question: str = "") -> Dict[str, Any]:
        """Get network data with hybrid approach - fast core + smart additions"""
        # Test mode: simulate network problems for testing
        if self.test_mode:
            logger.info("🧪 TEST MODE: Simulating network problems...")
            return self._get_simulated_problem_data()
        
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
    
    def _get_simulated_problem_data(self) -> Dict[str, Any]:
        """Simulate network problems for testing"""
        return {
            "wifi": {
                "status": "connected",
                "ssid": "TestNetwork",
                "signal_strength": "-65 dBm",  # Test signal between -60 and -70
                "interface": "en0",
                "ip_address": "192.168.1.100"
            },
            "connectivity": {
                "internet_connected": True,
                "dns_working": True,
                "latency": "45ms"
            },
            "performance": {
                "active_connections": 5,
                "network_quality": "fair"
            },
            "timestamp": time.time(),
            "diagnostics": {
                "network_interfaces": [],
                "routing_table": "unknown",
                "dns_resolution": {},
                "connectivity_tests": {}
            }
        }
    
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
            logger.info(f"🔍 Detecting network on platform: {system}")

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
                # For WSL/Linux, check if we have network connectivity
                try:
                    # Try iwconfig first (if available on real Linux)
                    result = subprocess.run(['iwconfig'], capture_output=True, text=True, timeout=2)
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
                except Exception as e:
                    # iwconfig not available (WSL) - check if we have internet via ip addr
                    logger.info(f"📡 iwconfig failed ({e}), trying WSL fallback with ip addr...")
                    try:
                        result = subprocess.run(['ip', 'addr'], capture_output=True, text=True, timeout=2)
                        logger.info(f"📡 ip addr result: returncode={result.returncode}, has_inet={'inet ' in result.stdout}")
                        if result.returncode == 0 and 'inet ' in result.stdout:
                            # We have network connectivity
                            wifi_info.update({
                                "status": "connected",
                                "ssid": "Network",  # Generic for WSL
                                "signal_strength": "unknown",
                                "interface": "eth0"
                            })
                            logger.info(f"✅ WSL network detected: {wifi_info}")
                    except Exception as e2:
                        logger.error(f"❌ WSL fallback also failed: {e2}")
            
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
            
            # DNS/Internet/Latency issues
            if any(word in question_lower for word in ['dns', 'internet', 'website', 'browser', 'slow', 'latency', 'ping', 'lag']):
                logger.info("🌐 Attempting to fix DNS/Internet/Latency issues...")
                
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

                # Try fixing latency issues specifically
                if 'latency' in question_lower or 'ping' in question_lower or 'lag' in question_lower:
                    try:
                        result = bash_cmd.fix_latency_issues()
                        fixes_attempted.append("Fix latency (flush routing cache)")
                        if "addressed" in result.lower():
                            fixes_successful.append("Latency optimizations applied")
                        else:
                            fixes_failed.append("Latency fix failed")
                    except Exception as e:
                        fixes_failed.append(f"Latency fix error: {e}")

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

            # Fastest band switching (Demo 5)
            if any(phrase in question_lower for phrase in ['fastest band', 'faster band', 'best band', 'switch band', 'better band', 'optimize band']):
                logger.info("⚡ Testing and switching to fastest WiFi band...")

                try:
                    result = bash_cmd.switch_to_fastest_band()
                    fixes_attempted.append("Test and switch to fastest band")

                    if result and isinstance(result, dict):
                        # Check for errors
                        if 'error' in result:
                            fixes_failed.append(f"Band switching failed: {result['error']}")
                        else:
                            original_speed = result.get('original_speed', 0)
                            final_speed = result.get('final_speed', 0)
                            improved = result.get('improved', False)
                            original_band = result.get('original_band', 'unknown')
                            final_band = result.get('final_band', 'unknown')
                            tested_speed = result.get('tested_speed', 0)

                            if original_speed == 0 or final_speed == 0:
                                fixes_failed.append(f"Speed test failed (original: {original_speed} Mbps, final: {final_speed} Mbps)")
                            elif improved:
                                fixes_successful.append(f"Switched to faster {final_band} band ({final_speed:.1f} Mbps vs {original_speed:.1f} Mbps)")
                            else:
                                fixes_successful.append(f"Stayed on {final_band} band (already fastest at {final_speed:.1f} Mbps)")
                    else:
                        fixes_failed.append("Band speed test returned invalid results")
                except Exception as e:
                    fixes_failed.append(f"Fastest band switching error: {e}")

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
        
        # Simplified flow: let generate_ai_response handle all logic
        fix_results = None
        
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

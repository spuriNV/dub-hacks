#!/usr/bin/env python3
"""
Simple Smart AI Chatbot UI
Streamlit interface for the AI brain
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime

# Configure Streamlit page
st.set_page_config(
    page_title="AI Network Brain",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
    }
    .chat-message.user {
        background-color: #2b313e;
        color: white;
    }
    .chat-message.assistant {
        background-color: #f0f2f6;
        color: black;
    }
    .chat-message .avatar {
        width: 2rem;
        height: 2rem;
        border-radius: 50%;
        margin-right: 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
    }
    .network-status {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 0.5rem;
    }
    .status-good { background-color: #4CAF50; }
    .status-warning { background-color: #FF9800; }
    .status-error { background-color: #F44336; }
    .ai-brain {
        background: linear-gradient(90deg, #ff6b6b 0%, #4ecdc4 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_url" not in st.session_state:
    st.session_state.api_url = "http://localhost:8088"

def get_network_status():
    """Get current network status from AI brain"""
    try:
        response = requests.get(f"{st.session_state.api_url}/network-status", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Network status error: {e}")
        return None

def get_ai_status():
    """Get AI brain status"""
    try:
        response = requests.get(f"{st.session_state.api_url}/ai-status", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"AI status error: {e}")
        return None

def send_chat_message(message):
    """Send message to AI brain and get response"""
    try:
        response = requests.post(
            f"{st.session_state.api_url}/chat",
            json={"message": message},
            timeout=15
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error connecting to AI brain: {e}")
        return None

def display_network_status():
    """Display current network status in sidebar"""
    st.sidebar.markdown("### 📊 Network Status")
    
    network_data = get_network_status()
    if network_data:
        wifi = network_data.get('network_data', {}).get('wifi', {})
        connectivity = network_data.get('network_data', {}).get('connectivity', {})
        performance = network_data.get('network_data', {}).get('performance', {})
        
        # WiFi Status
        wifi_status = wifi.get('status', 'unknown')
        wifi_ssid = wifi.get('ssid', 'Unknown')
        signal_strength = wifi.get('signal_strength', 'unknown')
        
        if wifi_status == 'connected':
            st.sidebar.markdown(f"""
            <div class="network-status">
                <h4>📶 WiFi Status</h4>
                <p><span class="status-indicator status-good"></span>Connected to: <strong>{wifi_ssid}</strong></p>
                <p>Signal: {signal_strength} dBm</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.sidebar.markdown(f"""
            <div class="network-status">
                <h4>📶 WiFi Status</h4>
                <p><span class="status-indicator status-error"></span>Not Connected</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Internet Status
        internet_connected = connectivity.get('internet_connected', False)
        latency = connectivity.get('latency', 'unknown')
        
        if internet_connected:
            st.sidebar.markdown(f"""
            <div class="network-status">
                <h4>🌐 Internet Status</h4>
                <p><span class="status-indicator status-good"></span>Connected</p>
                <p>Latency: {latency}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.sidebar.markdown(f"""
            <div class="network-status">
                <h4>🌐 Internet Status</h4>
                <p><span class="status-indicator status-error"></span>Not Connected</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Performance Status
        quality = performance.get('network_quality', 'unknown')
        active_connections = performance.get('active_connections', 0)
        
        st.sidebar.markdown(f"""
        <div class="network-status">
            <h4>⚡ Performance</h4>
            <p>Quality: {quality.title()}</p>
            <p>Active Connections: {active_connections}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.error("❌ Unable to connect to AI brain")

def display_ai_status():
    """Display AI brain status"""
    st.sidebar.markdown("### 🧠 AI Brain Status")
    
    ai_status = get_ai_status()
    if ai_status:
        ai_model = ai_status.get('ai_model_loaded', False)
        rag_enabled = ai_status.get('rag_enabled', False)
        knowledge_size = ai_status.get('knowledge_base_size', 0)
        
        if ai_model:
            st.sidebar.markdown(f"""
            <div class="ai-brain">
                <h4>🤖 AI Model</h4>
                <p><span class="status-indicator status-good"></span>distilgpt2 Loaded</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.sidebar.markdown(f"""
            <div class="ai-brain">
                <h4>🤖 AI Model</h4>
                <p><span class="status-indicator status-warning"></span>Rule-based Mode</p>
            </div>
            """, unsafe_allow_html=True)
        
        if rag_enabled:
            st.sidebar.markdown(f"""
            <div class="ai-brain">
                <h4>📚 RAG Knowledge</h4>
                <p><span class="status-indicator status-good"></span>{knowledge_size} Items Loaded</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.sidebar.markdown(f"""
            <div class="ai-brain">
                <h4>📚 RAG Knowledge</h4>
                <p><span class="status-indicator status-error"></span>Not Available</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.sidebar.error("❌ Unable to get AI brain status")

def main():
    """Main application"""
    # Header
    st.title("🧠 AI Network Brain")
    st.markdown("**Intelligent network analysis powered by RAG + lightweight AI model**")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🔧 Settings")
        api_url = st.text_input("API URL", value=st.session_state.api_url, help="URL of the AI brain API server")
        if api_url != st.session_state.api_url:
            st.session_state.api_url = api_url
            st.rerun()
        
        st.markdown("---")
        display_network_status()
        
        st.markdown("---")
        display_ai_status()
        
        st.markdown("---")
        st.markdown("### 💡 Ask the AI Brain")
        st.markdown("""
        **Try asking:**
        - "What's wrong with my WiFi?"
        - "My internet is slow, help me"
        - "How can I improve my signal?"
        - "Check my network security"
        - "Why is my connection dropping?"
        """)
    
    # Chat interface
    st.markdown("### 💬 Chat with AI Brain")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask the AI brain about your network..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI brain response
        with st.chat_message("assistant"):
            with st.spinner("🧠 AI brain is analyzing your network..."):
                response = send_chat_message(prompt)
                
                if response:
                    ai_response = response.get('response', 'Sorry, I could not process your request.')
                    st.markdown(ai_response)
                    
                    # Show AI brain status
                    ai_model_used = response.get('ai_model_used', False)
                    rag_enabled = response.get('rag_enabled', False)
                    
                    with st.expander("🧠 AI Brain Analysis Details"):
                        st.write(f"**AI Model Used:** {'Yes (distilgpt2)' if ai_model_used else 'No (rule-based)'}")
                        st.write(f"**RAG Knowledge:** {'Enabled' if rag_enabled else 'Disabled'}")
                        st.write(f"**Response Time:** {response.get('timestamp', 'Unknown')}")
                    
                    # Add AI response to messages
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                else:
                    st.error("❌ Failed to get response from AI brain. Please check if the API server is running.")
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**AI Brain:** RAG + distilgpt2")
    with col2:
        st.markdown("**Analysis:** Real-time CLI")
    with col3:
        st.markdown("**Version:** 7.0.0")

if __name__ == "__main__":
    main()

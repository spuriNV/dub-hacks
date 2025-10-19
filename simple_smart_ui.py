#!/usr/bin/env python3
"""
Professional Smart AI Chatbot UI
Enterprise-grade Streamlit interface for the AI brain
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

# Professional Custom CSS
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
    }
    
    .block-container {
        background: #ffffff;
        border-radius: 16px;
        padding: 2.5rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.15);
        max-width: 1400px;
    }
    
    /* Header Styles */
    .main-header {
        text-align: center;
        padding: 2.5rem 2rem;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 12px;
        margin-bottom: 2.5rem;
        box-shadow: 0 8px 24px rgba(30, 60, 114, 0.2);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        margin: 0;
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.85);
        font-size: 1rem;
        margin-top: 0.75rem;
        font-weight: 400;
        letter-spacing: 0.3px;
    }
    
    /* Chat Message Styles */
    .stChatMessage {
        background: transparent !important;
        padding: 1rem 0 !important;
    }
    
    [data-testid="stChatMessageContent"] {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 3px solid #2a5298;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    [data-testid="stChatMessageContent"]:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        transform: translateY(-1px);
    }
    
    .stChatMessage[data-testid*="user"] [data-testid="stChatMessageContent"] {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border-left: 3px solid #1e3c72;
    }
    
    /* Status Card Styles */
    .status-card {
        background: white;
        color: #1e3c72;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(30, 60, 114, 0.1);
    }
    
    .status-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
        border-color: rgba(30, 60, 114, 0.2);
    }
    
    .status-card h4 {
        margin: 0 0 1rem 0;
        font-size: 0.95rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #1e3c72;
    }
    
    .status-card p {
        margin: 0.5rem 0;
        font-size: 0.9rem;
        color: #4a5568;
        line-height: 1.6;
    }
    
    .status-card strong {
        color: #1e3c72;
        font-weight: 600;
    }
    
    /* Status Indicators */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 0.75rem;
        transition: all 0.3s ease;
    }
    
    .status-good { 
        background-color: #10b981;
        box-shadow: 0 0 8px rgba(16, 185, 129, 0.4);
    }
    .status-warning { 
        background-color: #f59e0b;
        box-shadow: 0 0 8px rgba(245, 158, 11, 0.4);
    }
    .status-error { 
        background-color: #ef4444;
        box-shadow: 0 0 8px rgba(239, 68, 68, 0.4);
    }
    
    /* Metric Cards */
    .metric-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #e5e7eb;
        margin-bottom: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .metric-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-color: #2a5298;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 600;
        color: #1e3c72;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        color: #6b7280;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    /* Sidebar Styles */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .status-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
    }
    
    /* Input Styles */
    .stTextInput input {
        border-radius: 8px;
        border: 2px solid #e5e7eb;
        padding: 0.75rem;
        font-size: 0.95rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput input:focus {
        border-color: #2a5298;
        box-shadow: 0 0 0 3px rgba(42, 82, 152, 0.1);
    }
    
    /* Chat Input */
    .stChatInput textarea {
        border-radius: 12px !important;
        border: 2px solid #e5e7eb !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stChatInput textarea:focus {
        border-color: #2a5298 !important;
        box-shadow: 0 0 0 3px rgba(42, 82, 152, 0.1) !important;
    }
    
    /* Button Styles */
    .stButton button {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-size: 0.95rem;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(30, 60, 114, 0.2);
        letter-spacing: 0.3px;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(30, 60, 114, 0.3);
    }
    
    /* Expander Styles */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white !important;
        border-radius: 8px;
        padding: 1rem;
        font-weight: 600;
        font-size: 0.9rem;
        letter-spacing: 0.3px;
    }
    
    .streamlit-expanderContent {
        border: 1px solid #e5e7eb;
        border-radius: 0 0 8px 8px;
        padding: 1rem;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0 1rem 0;
        color: #6b7280;
        border-top: 1px solid #e5e7eb;
        margin-top: 3rem;
    }
    
    .footer-badge {
        display: inline-block;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 0.5rem 1.25rem;
        border-radius: 20px;
        margin: 0 0.5rem;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 8px rgba(30, 60, 114, 0.2);
    }
    
    /* Loading Spinner */
    .stSpinner > div {
        border-top-color: #2a5298 !important;
    }
    
    /* Alert Messages */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid;
    }
    
    /* Suggestion Chips */
    .suggestion-chip {
        display: inline-block;
        background: rgba(255, 255, 255, 0.95);
        color: #1e3c72;
        padding: 0.6rem 1.25rem;
        border-radius: 20px;
        margin: 0.25rem;
        font-size: 0.85rem;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
        font-weight: 500;
    }
    
    .suggestion-chip:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        background: white;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e3c72;
        margin: 2rem 0 1rem 0;
        letter-spacing: -0.3px;
    }
    
    /* Smooth Transitions */
    * {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
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
        return None

def get_ai_status():
    """Get AI brain status"""
    try:
        response = requests.get(f"{st.session_state.api_url}/ai-status", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
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
        st.error(f"Connection Error: {str(e)}")
        return None

def display_network_status():
    """Display current network status in sidebar"""
    st.sidebar.markdown("### Network Dashboard")
    
    network_data = get_network_status()
    if network_data:
        wifi = network_data.get('network_data', {}).get('wifi', {})
        connectivity = network_data.get('network_data', {}).get('connectivity', {})
        performance = network_data.get('network_data', {}).get('performance', {})
        
        # WiFi Status
        wifi_status = wifi.get('status', 'unknown')
        wifi_ssid = wifi.get('ssid', 'Unknown')
        signal_strength = wifi.get('signal_strength', 'unknown')
        
        status_class = "status-good" if wifi_status == 'connected' else "status-error"
        status_text = "Connected" if wifi_status == 'connected' else "Disconnected"
        
        st.sidebar.markdown(f"""
        <div class="status-card">
            <h4>WiFi Connection</h4>
            <p><span class="status-indicator {status_class}"></span>{status_text}</p>
            <p><strong>Network:</strong> {wifi_ssid}</p>
            <p><strong>Signal Strength:</strong> {signal_strength} dBm</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Internet Status
        internet_connected = connectivity.get('internet_connected', False)
        latency = connectivity.get('latency', 'unknown')
        
        inet_status_class = "status-good" if internet_connected else "status-error"
        inet_status_text = "Online" if internet_connected else "Offline"
        
        st.sidebar.markdown(f"""
        <div class="status-card">
            <h4>Internet Status</h4>
            <p><span class="status-indicator {inet_status_class}"></span>{inet_status_text}</p>
            <p><strong>Latency:</strong> {latency}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Performance Status
        quality = performance.get('network_quality', 'unknown')
        active_connections = performance.get('active_connections', 0)
        
        quality_class = "status-good" if quality == "excellent" else "status-warning" if quality == "good" else "status-error"
        
        st.sidebar.markdown(f"""
        <div class="status-card">
            <h4>Performance Metrics</h4>
            <p><span class="status-indicator {quality_class}"></span>{quality.title()} Quality</p>
            <p><strong>Active Connections:</strong> {active_connections}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
        <div class="status-card">
            <h4>Connection Status</h4>
            <p><span class="status-indicator status-error"></span>Unable to reach AI brain</p>
            <p style="font-size: 0.85rem; opacity: 0.8;">Verify API server is running</p>
        </div>
        """, unsafe_allow_html=True)

def display_ai_status():
    """Display AI brain status"""
    st.sidebar.markdown("### AI Brain Status")
    
    ai_status = get_ai_status()
    if ai_status:
        ai_model = ai_status.get('ai_model_loaded', False)
        rag_enabled = ai_status.get('rag_enabled', False)
        knowledge_size = ai_status.get('knowledge_base_size', 0)
        
        model_status_class = "status-good" if ai_model else "status-warning"
        model_status_text = "distilgpt2 Active" if ai_model else "Rule-based Mode"
        
        st.sidebar.markdown(f"""
        <div class="status-card">
            <h4>AI Model</h4>
            <p><span class="status-indicator {model_status_class}"></span>{model_status_text}</p>
        </div>
        """, unsafe_allow_html=True)
        
        rag_status_class = "status-good" if rag_enabled else "status-error"
        rag_status_text = f"{knowledge_size} Items Loaded" if rag_enabled else "Not Available"
        
        st.sidebar.markdown(f"""
        <div class="status-card">
            <h4>Knowledge Base</h4>
            <p><span class="status-indicator {rag_status_class}"></span>{rag_status_text}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
        <div class="status-card">
            <h4>System Status</h4>
            <p><span class="status-indicator status-error"></span>Status unavailable</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main application"""
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>AI Network Brain</h1>
        <p>Intelligent Network Analysis • Real-time Monitoring • Smart Diagnostics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### Configuration")
        api_url = st.text_input("API Endpoint", value=st.session_state.api_url, 
                                help="URL of the AI brain API server")
        if api_url != st.session_state.api_url:
            st.session_state.api_url = api_url
            st.rerun()
        
        st.markdown("---")
        display_network_status()
        
        st.markdown("---")
        display_ai_status()
        
        st.markdown("---")
        st.markdown("### Quick Actions")
        st.markdown("""
        <div style="padding: 1rem 0;">
            <p style="font-size: 0.85rem; margin-bottom: 0.75rem; opacity: 0.9;">Common queries:</p>
            <div class="suggestion-chip">Check WiFi Status</div>
            <div class="suggestion-chip">Diagnose Slow Internet</div>
            <div class="suggestion-chip">Security Analysis</div>
            <div class="suggestion-chip">Network Statistics</div>
            <div class="suggestion-chip">Optimize Performance</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Main chat interface
    st.markdown('<p class="section-header">Conversation</p>', unsafe_allow_html=True)
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about your network..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI brain response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your network..."):
                response = send_chat_message(prompt)
                
                if response:
                    ai_response = response.get('response', 'Sorry, I could not process your request.')
                    st.markdown(ai_response)
                    
                    # Show AI brain analysis details
                    ai_model_used = response.get('ai_model_used', False)
                    rag_enabled = response.get('rag_enabled', False)
                    
                    with st.expander("View Analysis Details"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">AI Model</div>
                                <div class="metric-value">{'Active' if ai_model_used else 'Inactive'}</div>
                                <p style="margin: 0; color: #6b7280; font-size: 0.9rem;">{'distilgpt2' if ai_model_used else 'Rule-based'}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        with col2:
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">RAG Knowledge</div>
                                <div class="metric-value">{'Enabled' if rag_enabled else 'Disabled'}</div>
                                <p style="margin: 0; color: #6b7280; font-size: 0.9rem;">{'Context-aware' if rag_enabled else 'Standard'}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown(f"**Response Timestamp:** {response.get('timestamp', 'Unknown')}")
                    
                    # Add AI response to messages
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                else:
                    error_msg = "Unable to connect to AI brain. Please verify the API server is running and accessible."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Footer
    st.markdown("""
    <div class="footer">
        <span class="footer-badge">RAG + distilgpt2</span>
        <span class="footer-badge">Real-time Analysis</span>
        <span class="footer-badge">v7.0.0</span>
        <p style="margin-top: 1rem; font-size: 0.85rem;">
            Enterprise Network Intelligence Platform
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
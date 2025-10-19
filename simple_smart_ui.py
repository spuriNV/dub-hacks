#!/usr/bin/env python3
"""
Vercel-style AI Network Brain UI
Minimalist, modern chatbot interface inspired by Vercel AI Chatbot
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

# Vercel-inspired CSS
st.markdown("""
<style>
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Global Background */
    .main {
        background: #000000;
        padding: 0;
    }
    
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: #000000;
        border-right: 1px solid #262626;
        padding: 0;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding: 1rem;
    }
    
    /* Sidebar Header */
    .sidebar-header {
        padding: 1rem 0.75rem;
        border-bottom: 1px solid #262626;
        margin-bottom: 1rem;
    }
    
    .sidebar-header h3 {
        color: #ffffff;
        font-size: 0.875rem;
        font-weight: 600;
        margin: 0;
        letter-spacing: -0.01em;
    }
    
    /* New Chat Button */
    .new-chat-btn {
        width: 100%;
        background: #ffffff;
        color: #000000;
        border: none;
        border-radius: 0.5rem;
        padding: 0.625rem 1rem;
        font-size: 0.875rem;
        font-weight: 500;
        cursor: pointer;
        transition: background 0.2s;
        margin-bottom: 1.5rem;
    }
    
    .new-chat-btn:hover {
        background: #f5f5f5;
    }
    
    /* Chat History Item */
    .chat-history-item {
        padding: 0.625rem 0.75rem;
        margin: 0.125rem 0;
        border-radius: 0.5rem;
        color: #a3a3a3;
        font-size: 0.875rem;
        cursor: pointer;
        transition: all 0.2s;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    
    .chat-history-item:hover {
        background: #1a1a1a;
        color: #ffffff;
    }
    
    .chat-history-item.active {
        background: #1a1a1a;
        color: #ffffff;
    }
    
    /* Status Badge */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        padding: 0.25rem 0.625rem;
        background: #1a1a1a;
        border: 1px solid #262626;
        border-radius: 1rem;
        font-size: 0.75rem;
        color: #a3a3a3;
        margin: 0.25rem 0.25rem 0.25rem 0;
    }
    
    .status-dot {
        width: 0.5rem;
        height: 0.5rem;
        border-radius: 50%;
        background: #22c55e;
    }
    
    .status-dot.warning {
        background: #eab308;
    }
    
    .status-dot.error {
        background: #ef4444;
    }
    
    /* Main Chat Area */
    .chat-container {
        max-width: 48rem;
        margin: 0 auto;
        padding: 2rem 1rem;
        min-height: 100vh;
    }
    
    /* Welcome Screen */
    .welcome-screen {
        text-align: center;
        padding: 4rem 2rem;
        color: #ffffff;
    }
    
    .welcome-screen h1 {
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .welcome-screen p {
        color: #a3a3a3;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    
    /* Suggestion Cards */
    .suggestion-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 0.75rem;
        margin-top: 2rem;
    }
    
    .suggestion-card {
        background: #1a1a1a;
        border: 1px solid #262626;
        border-radius: 0.75rem;
        padding: 1rem;
        cursor: pointer;
        transition: all 0.2s;
        text-align: left;
    }
    
    .suggestion-card:hover {
        background: #262626;
        border-color: #404040;
        transform: translateY(-2px);
    }
    
    .suggestion-card h4 {
        color: #ffffff;
        font-size: 0.875rem;
        font-weight: 500;
        margin: 0 0 0.25rem 0;
    }
    
    .suggestion-card p {
        color: #737373;
        font-size: 0.75rem;
        margin: 0;
    }
    
    /* Chat Messages */
    .stChatMessage {
        background: transparent !important;
        padding: 1.5rem 0 !important;
        border-bottom: 1px solid #1a1a1a;
    }
    
    [data-testid="stChatMessageContent"] {
        background: transparent !important;
        color: #ffffff !important;
        padding: 0 !important;
        box-shadow: none !important;
        border: none !important;
        font-size: 0.9375rem;
        line-height: 1.7;
    }
    
    /* User Message */
    .stChatMessage[data-testid*="user"] [data-testid="stChatMessageContent"] {
        color: #a3a3a3 !important;
    }
    
    /* Chat Input */
    .stChatInput {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: #000000;
        border-top: 1px solid #262626;
        padding: 1rem;
        z-index: 100;
    }
    
    .stChatInput > div {
        max-width: 48rem;
        margin: 0 auto;
    }
    
    .stChatInput textarea {
        background: #1a1a1a !important;
        border: 1px solid #262626 !important;
        border-radius: 0.75rem !important;
        color: #ffffff !important;
        font-size: 0.9375rem !important;
        padding: 0.875rem 1rem !important;
        resize: none !important;
    }
    
    .stChatInput textarea:focus {
        border-color: #404040 !important;
        box-shadow: none !important;
    }
    
    .stChatInput textarea::placeholder {
        color: #737373 !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #404040 !important;
        border-top-color: #ffffff !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #1a1a1a !important;
        border: 1px solid #262626 !important;
        border-radius: 0.5rem !important;
        color: #a3a3a3 !important;
        font-size: 0.8125rem !important;
        padding: 0.625rem 0.875rem !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: #262626 !important;
        border-color: #404040 !important;
    }
    
    .streamlit-expanderContent {
        background: #0a0a0a;
        border: 1px solid #262626;
        border-top: none;
        border-radius: 0 0 0.5rem 0.5rem;
        padding: 1rem;
    }
    
    /* Metric Display */
    .metric-row {
        display: flex;
        gap: 0.75rem;
        margin-top: 0.75rem;
    }
    
    .metric-item {
        flex: 1;
        background: #1a1a1a;
        border: 1px solid #262626;
        border-radius: 0.5rem;
        padding: 0.75rem;
    }
    
    .metric-label {
        color: #737373;
        font-size: 0.75rem;
        margin-bottom: 0.25rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .metric-value {
        color: #ffffff;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    /* Settings Section */
    .settings-section {
        padding: 1rem 0;
        border-top: 1px solid #262626;
        margin-top: auto;
    }
    
    .settings-item {
        padding: 0.625rem 0.75rem;
        color: #a3a3a3;
        font-size: 0.875rem;
        cursor: pointer;
        border-radius: 0.5rem;
        transition: all 0.2s;
    }
    
    .settings-item:hover {
        background: #1a1a1a;
        color: #ffffff;
    }
    
    /* Text Input in Sidebar */
    [data-testid="stSidebar"] .stTextInput input {
        background: #1a1a1a !important;
        border: 1px solid #262626 !important;
        color: #ffffff !important;
        font-size: 0.875rem !important;
        border-radius: 0.5rem !important;
        padding: 0.5rem 0.75rem !important;
    }
    
    [data-testid="stSidebar"] .stTextInput input:focus {
        border-color: #404040 !important;
        box-shadow: none !important;
    }
    
    [data-testid="stSidebar"] label {
        color: #a3a3a3 !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
    }
    
    /* Error Messages */
    .stAlert {
        background: #1a1a1a !important;
        border: 1px solid #262626 !important;
        border-radius: 0.5rem !important;
        color: #ef4444 !important;
        font-size: 0.875rem !important;
    }
    
    /* Section Divider */
    .section-divider {
        height: 1px;
        background: #262626;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_url" not in st.session_state:
    st.session_state.api_url = "http://localhost:8088"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

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
        return None

def render_sidebar():
    """Render Vercel-style sidebar"""
    with st.sidebar:
        st.markdown('<div class="sidebar-header"><h3>AI Network Brain</h3></div>', unsafe_allow_html=True)
        
        # New Chat Button
        if st.button("New Chat", key="new_chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        # Chat History
        st.markdown('<p style="color: #737373; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin: 1rem 0 0.5rem 0;">Recent</p>', unsafe_allow_html=True)
        
        if st.session_state.chat_history:
            for i, chat in enumerate(st.session_state.chat_history[-10:]):
                st.markdown(f'<div class="chat-history-item">{chat}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<p style="color: #737373; font-size: 0.8125rem; padding: 0.5rem 0.75rem;">No chat history</p>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Network Status
        st.markdown('<p style="color: #737373; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin: 1rem 0 0.5rem 0;">Status</p>', unsafe_allow_html=True)
        
        network_data = get_network_status()
        ai_data = get_ai_status()
        
        if network_data:
            wifi = network_data.get('network_data', {}).get('wifi', {})
            connectivity = network_data.get('network_data', {}).get('connectivity', {})
            
            wifi_status = wifi.get('status', 'unknown')
            internet_connected = connectivity.get('internet_connected', False)
            
            wifi_class = "status-dot" if wifi_status == 'connected' else "status-dot error"
            internet_class = "status-dot" if internet_connected else "status-dot error"
            
            st.markdown(f'<div class="status-badge"><span class="{wifi_class}"></span>WiFi {wifi_status.title()}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="status-badge"><span class="{internet_class}"></span>Internet {"Online" if internet_connected else "Offline"}</div>', unsafe_allow_html=True)
        
        if ai_data:
            ai_model = ai_data.get('ai_model_loaded', False)
            rag_enabled = ai_data.get('rag_enabled', False)
            
            model_class = "status-dot" if ai_model else "status-dot warning"
            rag_class = "status-dot" if rag_enabled else "status-dot error"
            
            st.markdown(f'<div class="status-badge"><span class="{model_class}"></span>AI {"Active" if ai_model else "Rule-based"}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="status-badge"><span class="{rag_class}"></span>RAG {"Enabled" if rag_enabled else "Disabled"}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Settings
        st.markdown('<p style="color: #737373; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin: 1rem 0 0.5rem 0;">Settings</p>', unsafe_allow_html=True)
        
        api_url = st.text_input("API Endpoint", value=st.session_state.api_url, label_visibility="collapsed", placeholder="http://localhost:8088")
        if api_url != st.session_state.api_url:
            st.session_state.api_url = api_url
            st.rerun()

def render_welcome_screen():
    """Render welcome screen when no messages"""
    st.markdown("""
    <div class="welcome-screen">
        <h1>AI Network Brain</h1>
        <p>Intelligent network analysis and diagnostics</p>
        
        <div class="suggestion-grid">
            <div class="suggestion-card">
                <h4>Check WiFi Status</h4>
                <p>Analyze your wireless connection</p>
            </div>
            <div class="suggestion-card">
                <h4>Diagnose Slow Internet</h4>
                <p>Find performance bottlenecks</p>
            </div>
            <div class="suggestion-card">
                <h4>Security Analysis</h4>
                <p>Check network security settings</p>
            </div>
            <div class="suggestion-card">
                <h4>Network Statistics</h4>
                <p>View detailed metrics</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application"""
    render_sidebar()
    
    # Main chat area
    if not st.session_state.messages:
        render_welcome_screen()
    else:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about your network..."):
        # Add to chat history
        if prompt not in st.session_state.chat_history:
            st.session_state.chat_history.append(prompt[:50] + "..." if len(prompt) > 50 else prompt)
        
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI brain response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                response = send_chat_message(prompt)
                
                if response:
                    ai_response = response.get('response', 'Unable to process request.')
                    st.markdown(ai_response)
                    
                    # Analysis details
                    ai_model_used = response.get('ai_model_used', False)
                    rag_enabled = response.get('rag_enabled', False)
                    
                    with st.expander("Analysis Details"):
                        st.markdown(f"""
                        <div class="metric-row">
                            <div class="metric-item">
                                <div class="metric-label">AI Model</div>
                                <div class="metric-value">{'distilgpt2' if ai_model_used else 'Rule-based'}</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-label">RAG Status</div>
                                <div class="metric-value">{'Enabled' if rag_enabled else 'Disabled'}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                else:
                    error_msg = "Unable to connect to AI brain. Check API server status."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    main()
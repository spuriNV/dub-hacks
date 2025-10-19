import streamlit as st
import requests
import time

st.set_page_config(
    page_title="AI Network Brain",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Vercel-inspired CSS applied to page
st.markdown("""
<style>
/* ... [Paste your full CSS here: unchanged] ... */
</style>
""", unsafe_allow_html=True)

# Session state setup
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_url" not in st.session_state:
    st.session_state.api_url = "http://localhost:8088"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Utility functions
def get_network_status():
    try:
        response = requests.get(f"{st.session_state.api_url}/network-status", timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None

def get_ai_status():
    try:
        response = requests.get(f"{st.session_state.api_url}/ai-status", timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None

def send_chat_message(message):
    try:
        response = requests.post(
            f"{st.session_state.api_url}/chat",
            json={"message": message},
            timeout=15
        )
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None

def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="sidebar-header"><h3>AI Network Brain</h3></div>', unsafe_allow_html=True)
        new_clicked = st.button("New Chat", key="new_chat", use_container_width=True)
        st.markdown('<p style="color: #737373; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin: 1rem 0 0.5rem 0;">Recent</p>', unsafe_allow_html=True)
        if st.session_state.chat_history:
            for chat in st.session_state.chat_history[-10:]:
                st.markdown(f'<div class="chat-history-item">{chat["summary"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<p style="color: #737373; font-size: 0.8125rem; padding: 0.5rem 0.75rem;">No chat history</p>', unsafe_allow_html=True)
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
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
        st.markdown('<p style="color: #737373; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin: 1rem 0 0.5rem 0;">Settings</p>', unsafe_allow_html=True)
        api_url = st.text_input("API Endpoint", value=st.session_state.api_url, label_visibility="collapsed", placeholder="http://localhost:8088")
        # Rerun only if API changes
        if api_url != st.session_state.api_url:
            st.session_state.api_url = api_url
            st.experimental_rerun()
        # Return flag for new chat
        return new_clicked

def render_welcome_screen():
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
    new_clicked = render_sidebar()
    # Reset everything for a new chat
    if new_clicked:
        st.session_state.messages = []
        st.session_state.chat_history.append({
            "summary": "New chat started",
            "full": [],
        })
        st.experimental_rerun()
    st.markdown('<div class="main">', unsafe_allow_html=True)
    if not st.session_state.messages:
        render_welcome_screen()
    else:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    # Chat input
    prompt = st.chat_input("Ask about your network...")
    if prompt:
        # Add to chat history as a summary (show first N chars, keeps track of all prompts)
        st.session_state.chat_history.append({
            "summary": prompt[:50] + ("..." if len(prompt) > 50 else ""),
            "full": prompt,
        })
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        # AI response block
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                response = send_chat_message(prompt)
                if response:
                    ai_response = response.get('response', 'Unable to process request.')
                    st.markdown(ai_response)
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

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

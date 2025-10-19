# simple_smart_ui.py
# Streamlit single-file port of your React UI (Dashboard, Layout, Panels, Chat)
# Features preserved:
# - Settings (API URL, Voice mode)
# - Network/Internet/Performance status panels
# - Chat history (user/assistant), AI call to /chat, optional audio_url playback
# - Suggestions, error display, mic (simulated) + audio upload
# - Glassmorphism styling, gradient background, icons(ish)

import time
import json
from datetime import datetime
from typing import List, Dict, Optional

import requests
import streamlit as st

# -----------------------------
# Page + Global Styling (Layout)
# -----------------------------
st.set_page_config(
    page_title="AI Network Brain",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject styles (gradient bg + glassmorphism + small helpers)
st.markdown("""
<style>
:root{
  --panel: rgba(255,255,255,0.08);
  --border: rgba(255,255,255,0.2);
  --text: #ffffff;
  --muted: rgba(180, 200, 255, 0.85);
}

html, body, .stApp {
  height: 100%;
  background: linear-gradient(135deg, #0f2027 0%, #203a43 25%, #2c5364 50%, #1a2a6c 75%, #0f1642 100%) !important;
  color: var(--text);
}
.block-container { padding-top: 0.8rem; }

.glass {
  backdrop-filter: blur(18px);
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 16px;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
}

.card-title {
  font-weight: 600;
  font-size: 0.95rem;
}

.badge {
  display: inline-block;
  padding: 0.15rem 0.45rem;
  border-radius: 9999px;
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.25);
  font-size: 0.7rem;
  color: #fff;
}

.msg-bubble { padding: 0.75rem 0.9rem; border-radius: 14px; margin-bottom: 8px; }
.msg-user { background: rgba(96,165,250,0.25); border: 1px solid rgba(96,165,250,0.45); }
.msg-assistant { background: rgba(167,139,250,0.25); border: 1px solid rgba(167,139,250,0.45); }
.small { font-size: 0.8rem; color: var(--muted); }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Session bootstrap (user, settings, messages, network)
# -----------------------------
if "user" not in st.session_state:
    st.session_state.user = {"email": "user@example.com"}

if "settings" not in st.session_state:
    st.session_state.settings = {
        "api_url": "http://localhost:8088",
        "voice_mode_enabled": False,
        "user_email": st.session_state.user["email"],
    }

if "messages" not in st.session_state:
    st.session_state.messages: List[Dict] = []

if "network_data" not in st.session_state:
    st.session_state.network_data: Optional[Dict] = None

if "ai_data" not in st.session_state:
    st.session_state.ai_data: Optional[Dict] = None

if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

if "error" not in st.session_state:
    st.session_state.error: Optional[str] = None

if "chat_input_text" not in st.session_state:
    st.session_state.chat_input_text = ""


# -----------------------------
# Data access helpers (mutations)
# -----------------------------
def add_message(role: str, content: str, audio_url: Optional[str] = None,
                ai_model_used: Optional[bool] = None, rag_enabled: Optional[bool] = None):
    st.session_state.messages.append({
        "id": f"m{len(st.session_state.messages)+1}",
        "role": role,
        "content": content,
        "audio_url": audio_url,
        "ai_model_used": ai_model_used if ai_model_used is not None else False,
        "rag_enabled": rag_enabled if rag_enabled is not None else False,
        "created_at": datetime.utcnow().isoformat()
    })


def update_settings(new_settings: Dict):
    st.session_state.settings.update(new_settings)


# -----------------------------
# Remote status fetchers
# -----------------------------
def fetch_network_status():
    api = st.session_state.settings.get("api_url")
    if not api:
        return
    try:
        r = requests.get(f"{api}/network-status", timeout=4)
        if r.ok:
            data = r.json()
            st.session_state.network_data = data.get("network_data")
    except Exception:
        pass


def fetch_ai_status():
    api = st.session_state.settings.get("api_url")
    if not api:
        return
    try:
        r = requests.get(f"{api}/ai-status", timeout=4)
        if r.ok:
            st.session_state.ai_data = r.json()
    except Exception:
        pass


# -----------------------------
# Chat interaction (POST /chat)
# -----------------------------
def send_to_ai_brain(message: str, generate_audio: bool):
    api = st.session_state.settings.get("api_url")
    if not api:
        raise RuntimeError("API URL is not set.")
    r = requests.post(
        f"{api}/chat",
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "message": message,
            "generate_audio": generate_audio
        }),
        timeout=10
    )
    if not r.ok:
        raise RuntimeError(f"AI server error: {r.status_code}")
    return r.json()


# -----------------------------
# UI Components (Streamlit equivalents)
# -----------------------------
def component_network_status(network_data: Optional[Dict]):
    icon_map = {"wifi": "📶"}
    badge_color = {"good": "#4ade80", "error": "#f87171"}
    
    status = (network_data or {}).get("wifi", {}).get("status")
    dot_status = "good" if status == "connected" else "error"
    dot_color = badge_color[dot_status]
    
    st.markdown(f"""
    <div class="glass" style="padding:16px;margin-bottom:12px;">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
        <div style="width:40px;height:40px;border-radius:12px;background:rgba(255,255,255,0.10);
             border:1px solid var(--border);display:flex;align-items:center;justify-content:center;">
          <div style="font-size:18px">{icon_map['wifi']}</div>
        </div>
        <div style="flex:1"><div class="card-title">Network Status</div></div>
        <span style="display:inline-block;width:10px;height:10px;border-radius:50%;
        background:{dot_color};box-shadow:0 0 10px {dot_color};"></span>
      </div>
    """, unsafe_allow_html=True)
    
    if not network_data:
        st.markdown('<div class="small" style="color:#fecaca">Unable to connect to AI brain</div>', unsafe_allow_html=True)
    else:
        wifi = network_data.get("wifi", {})
        if wifi.get("status") == "connected":
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Connected to:**")
            with c2:
                st.markdown(f"{wifi.get('ssid','Unknown')}")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Signal:**")
            with c2:
                st.markdown(f"{wifi.get('signal_strength','N/A')} dBm")
        else:
            st.markdown('<div class="small" style="color:#fecaca">Not Connected</div>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


def component_internet_status(network_data: Optional[Dict]):
    icon = "🌐"
    badge_color = {"good": "#4ade80", "error": "#f87171"}
    
    connectivity = (network_data or {}).get("connectivity", {})
    dot_status = "good" if connectivity.get("internet_connected") else "error"
    dot_color = badge_color[dot_status]
    
    st.markdown(f"""
    <div class="glass" style="padding:16px;margin-bottom:12px;">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
        <div style="width:40px;height:40px;border-radius:12px;background:rgba(255,255,255,0.10);
             border:1px solid var(--border);display:flex;align-items:center;justify-content:center;">
          <div style="font-size:18px">{icon}</div>
        </div>
        <div style="flex:1"><div class="card-title">Internet Status</div></div>
        <span style="display:inline-block;width:10px;height:10px;border-radius:50%;
        background:{dot_color};box-shadow:0 0 10px {dot_color};"></span>
      </div>
    """, unsafe_allow_html=True)
    
    if not network_data:
        st.markdown('<div class="small" style="color:#fecaca">Unable to connect to AI brain</div>', unsafe_allow_html=True)
    else:
        if connectivity.get("internet_connected"):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Status:**")
            with c2:
                st.markdown("Connected")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Latency:**")
            with c2:
                st.markdown(f"{connectivity.get('latency','N/A')}")
        else:
            st.markdown('<div class="small" style="color:#fecaca">Not Connected</div>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


def component_performance_status(network_data: Optional[Dict]):
    icon = "⚡"
    badge_color = {"good": "#4ade80", "warning": "#fbbf24", "error": "#f87171"}
    
    performance = (network_data or {}).get("performance", {})
    quality = performance.get("network_quality")
    
    if quality in ("excellent", "good"):
        dot_status = "good"
    elif quality == "fair":
        dot_status = "warning"
    else:
        dot_status = "error"
    
    dot_color = badge_color.get(dot_status, badge_color["error"])
    
    st.markdown(f"""
    <div class="glass" style="padding:16px;margin-bottom:12px;">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
        <div style="width:40px;height:40px;border-radius:12px;background:rgba(255,255,255,0.10);
             border:1px solid var(--border);display:flex;align-items:center;justify-content:center;">
          <div style="font-size:18px">{icon}</div>
        </div>
        <div style="flex:1"><div class="card-title">Performance</div></div>
        <span style="display:inline-block;width:10px;height:10px;border-radius:50%;
        background:{dot_color};box-shadow:0 0 10px {dot_color};"></span>
      </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Quality:**")
    with c2:
        st.markdown(f"{(quality or 'Unknown').capitalize() if isinstance(quality,str) else 'Unknown'}")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Active Connections:**")
    with c2:
        st.markdown(f"{performance.get('active_connections', 0)}")
    
    st.markdown("</div>", unsafe_allow_html=True)


def component_settings_panel(settings: Dict):
    icon = "⚙️"
    
    st.markdown(f"""
    <div class="glass" style="padding:16px;margin-bottom:12px;">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
        <div style="width:40px;height:40px;border-radius:12px;background:rgba(255,255,255,0.10);
             border:1px solid var(--border);display:flex;align-items:center;justify-content:center;">
          <div style="font-size:18px">{icon}</div>
        </div>
        <div style="flex:1"><div class="card-title">Settings</div></div>
      </div>
    """, unsafe_allow_html=True)
    
    api_url = st.text_input("API URL", 
                           value=settings.get("api_url","http://localhost:8088"),
                           help="http://localhost:8088",
                           key="settings_api_url")
    
    voice = st.toggle("Voice Responses", 
                     value=settings.get("voice_mode_enabled", False), 
                     help="Enable TTS audio in /chat",
                     key="settings_voice")
    
    # Update on change
    changed = (api_url != settings.get("api_url")) or (voice != settings.get("voice_mode_enabled"))
    if changed:
        update_settings({"api_url": api_url, "voice_mode_enabled": voice})
    
    st.markdown("</div>", unsafe_allow_html=True)


def component_suggestions(on_select):
    st.markdown("""
    <div class="glass" style="padding:16px;margin-bottom:12px;background: linear-gradient(135deg, rgba(245,158,11,0.2), rgba(253,224,71,0.2));">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
        <span>💡</span><div class="card-title">Ask the AI Brain</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    suggestions = [
        "What's wrong with my WiFi?",
        "My internet is slow, help me",
        "How can I improve my signal?",
        "Check my network security",
        "Why is my connection dropping?",
    ]
    
    for i, s in enumerate(suggestions):
        if st.button(f"✨ {s}", key=f"sugg_{i}", use_container_width=True):
            on_select(s)
            st.rerun()


def component_message_bubble(message: Dict, index: int):
    role = message.get("role", "assistant")
    content = message.get("content", "")
    audio_url = message.get("audio_url")
    ai_model_used = message.get("ai_model_used", False)
    rag_enabled = message.get("rag_enabled", False)
    
    left_pad = 1 if role == "assistant" else 2
    right_pad = 2 if role == "assistant" else 1
    
    col = st.columns([left_pad, 8, right_pad])
    with col[1]:
        css_class = "msg-assistant" if role == "assistant" else "msg-user"
        header = '🧠 Assistant' if role=='assistant' else '👤 You'
        
        st.markdown(f"""
        <div class="msg-bubble {css_class}">
            <strong>{header}</strong>
            <div style="margin-top:6px;">{content}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show flags
        flag_line = []
        if ai_model_used:
            flag_line.append("Model: **ON**")
        if rag_enabled:
            flag_line.append("RAG: **ON**")
        if flag_line:
            st.markdown(f"<div class='small'>{' • '.join(flag_line)}</div>", unsafe_allow_html=True)
        
        # Audio playback
        if audio_url:
            try:
                st.audio(audio_url)
            except Exception:
                st.markdown(f"<div class='small' style='color:#fecaca'>Audio unavailable: {audio_url}</div>",
                          unsafe_allow_html=True)


def component_chat_input(on_send, on_voice, is_processing: bool):
    # Text area with proper key management
    msg = st.text_area("",
                      value=st.session_state.chat_input_text,
                      key="chat_textarea",
                      placeholder="Ask the AI brain about your network...",
                      disabled=is_processing,
                      label_visibility="collapsed",
                      help="Type your message here",
                      height=110)
    
    c1, c2, c3 = st.columns([2,2,4])
    
    with c1:
        if st.button("📨 Send", 
                    disabled=is_processing or not msg.strip(),
                    use_container_width=True):
            on_send(msg)
            st.session_state.chat_input_text = ""
            st.rerun()
    
    with c2:
        if st.button("⏺️ Record (sim)" if not is_processing else "Processing...",
                    disabled=is_processing,
                    use_container_width=True):
            on_voice("SIMULATED_RECORDING")
            st.rerun()
    
    with c3:
        uploaded = st.file_uploader("Upload audio", 
                                   type=["mp3","wav","m4a","ogg","webm"], 
                                   label_visibility="collapsed",
                                   key="audio_upload")
        if uploaded is not None and st.button("🗣️ Transcribe", use_container_width=True):
            on_voice(uploaded)
            st.rerun()
    
    st.markdown('<div class="small">Type your message and press Send • Use Record for voice input (simulated) • Upload audio files for transcription</div>',
                unsafe_allow_html=True)


# -----------------------------
# Handlers (mirror React handlers)
# -----------------------------
def handle_send_message(content: str):
    if not st.session_state.user or not content.strip():
        return
    
    st.session_state.is_processing = True
    st.session_state.error = None
    
    try:
        # Add user message
        add_message("user", content)
        
        # Send to AI brain
        data = send_to_ai_brain(
            message=content,
            generate_audio=bool(st.session_state.settings.get("voice_mode_enabled"))
        )
        
        # Add AI response
        audio_url = None
        if data.get("audio_url"):
            api_url = st.session_state.settings['api_url']
            audio_url = f"{api_url}{data['audio_url']}" if not data['audio_url'].startswith('http') else data['audio_url']
        
        add_message(
            "assistant",
            data.get("response") or "Sorry, I could not process your request.",
            audio_url=audio_url,
            ai_model_used=data.get("ai_model_used", False),
            rag_enabled=data.get("rag_enabled", False)
        )
    except Exception as e:
        st.session_state.error = f"Failed to communicate with AI brain: {str(e)}"
        add_message("assistant", "Sorry, I'm having trouble connecting right now. Please try again later.")
    finally:
        st.session_state.is_processing = False


def handle_voice_input(source):
    st.session_state.is_processing = True
    st.session_state.error = None
    
    try:
        # Simulated transcription
        time.sleep(1)
        transcription = "This is a simulated voice transcription. In production, this would use Whisper or a similar service."
        handle_send_message(transcription)
    except Exception as e:
        st.session_state.error = f"Failed to process voice input: {str(e)}"
    finally:
        st.session_state.is_processing = False


# -----------------------------
# Header / Footer (Layout port)
# -----------------------------
def header():
    st.markdown("""
    <div class="glass" style="padding:14px 18px;margin-bottom:18px;border-radius:0 0 16px 16px;">
      <div style="display:flex;align-items:center;gap:12px;">
        <div style="width:48px;height:48px;border-radius:16px;background:linear-gradient(135deg,#3b82f6,#4f46e5);
             border:1px solid var(--border);display:flex;align-items:center;justify-content:center;box-shadow: 0 0 30px rgba(59,130,246,0.5);">
          <div style="font-size:22px;">🧠</div>
        </div>
        <div>
          <div style="font-size:22px;font-weight:700;color:#fff;">AI Network Brain</div>
          <div class="small">Intelligent network analysis powered by RAG + AI</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def footer():
    st.markdown("""
    <div class="glass" style="padding:12px 16px;margin-top:18px;border-radius:16px 16px 0 0;">
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;text-align:center;" class="small">
        <div><span class="badge" style="margin-right:6px;">AI Brain</span> RAG + distilgpt2</div>
        <div><span class="badge" style="margin-right:6px;">Analysis</span> Real-time CLI</div>
        <div><span class="badge" style="margin-right:6px;">Version</span> 8.0.0</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------
# Main "Dashboard" page
# -----------------------------
def dashboard():
    header()
    
    # Sidebar column (left) + Main (right)
    left, right = st.columns([1, 3])
    
    with left:
        component_settings_panel(st.session_state.settings)
        
        # Manual refresh
        if st.button("🔄 Refresh status", use_container_width=True):
            fetch_network_status()
            fetch_ai_status()
            st.rerun()
        
        component_network_status(st.session_state.network_data)
        component_internet_status(st.session_state.network_data)
        component_performance_status(st.session_state.network_data)
        component_suggestions(lambda s: handle_send_message(s))
    
    with right:
        # Chat panel
        st.markdown('<div class="glass" style="padding:18px;min-height:600px;">',
                   unsafe_allow_html=True)
        
        if len(st.session_state.messages) == 0 and not st.session_state.is_processing:
            st.markdown("""
            <div style="display:flex;align-items:center;justify-content:center;height:480px;">
              <div style="text-align:center;">
                <div style="width:80px;height:80px;margin:0 auto 14px;border-radius:20px;
                     background:linear-gradient(135deg,rgba(59,130,246,0.3),rgba(99,102,241,0.3));
                     border:1px solid var(--border);display:flex;align-items:center;justify-content:center;">
                  <div style="font-size:30px;">🧠</div>
                </div>
                <div style="font-size:18px;font-weight:600;">Welcome to AI Network Brain</div>
                <div class="small">Ask me anything about your network!</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Scrollable messages area
            message_container = st.container()
            with message_container:
                for idx, m in enumerate(st.session_state.messages):
                    component_message_bubble(m, idx)
        
        # Processing indicator
        if st.session_state.is_processing:
            with st.spinner("AI brain is analyzing..."):
                time.sleep(0.1)
        
        # Error alert
        if st.session_state.error:
            st.error(st.session_state.error)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Chat input outside the glass panel
        st.markdown("<div style='margin-top:12px;'>", unsafe_allow_html=True)
        component_chat_input(handle_send_message, handle_voice_input, st.session_state.is_processing)
        st.markdown("</div>", unsafe_allow_html=True)
    
    footer()


# -----------------------------
# Initial status fetch
# -----------------------------
if "last_api_url" not in st.session_state:
    st.session_state.last_api_url = st.session_state.settings.get("api_url")

if st.session_state.last_api_url != st.session_state.settings.get("api_url"):
    st.session_state.last_api_url = st.session_state.settings.get("api_url")
    fetch_network_status()
    fetch_ai_status()

# Try initial fetch
if st.session_state.network_data is None:
    fetch_network_status()
if st.session_state.ai_data is None:
    fetch_ai_status()

# -----------------------------
# Run the app
# -----------------------------
dashboard()
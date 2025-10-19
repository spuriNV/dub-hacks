# simple_smart_ui.py
# Streamlit single-file port of your React UI (Dashboard, Layout, Panels, Chat)
# Features preserved:
# - Settings (API URL, Voice mode)
# - Network/Internet/Performance status panels
# - Chat history (user/assistant), AI call to /chat, optional audio_url playback
# - Real voice recording with Whisper transcription
# - Glassmorphism styling, gradient background, modern UI

import time
import json
import os
import subprocess
from datetime import datetime
from typing import List, Dict, Optional

import requests
import streamlit as st
from audio_recorder_streamlit import audio_recorder

# -----------------------------
# Voice Recording & Transcription Functions
# -----------------------------
def save_audio_recording(audio_bytes):
    """Save audio recording to recordings folder"""
    try:
        recordings_dir = os.path.join(os.path.dirname(__file__), "recordings")
        os.makedirs(recordings_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.wav"
        filepath = os.path.join(recordings_dir, filename)
        
        with open(filepath, "wb") as f:
            f.write(audio_bytes)
        
        return filepath, filename
    except Exception as e:
        st.session_state.error = f"Error saving recording: {e}"
        return None, None


def convert_to_wav_16khz(input_file):
    """Convert audio to 16kHz WAV format for whisper.cpp"""
    try:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_16khz.wav"
        
        cmd = [
            "ffmpeg",
            "-i", input_file,
            "-ar", "16000",
            "-ac", "1",
            "-c:a", "pcm_s16le",
            "-y",
            output_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return output_file
        else:
            st.session_state.error = f"FFmpeg error: {result.stderr}"
            return None
    except Exception as e:
        st.session_state.error = f"Error converting audio: {e}"
        return None


def transcribe_with_whisper(audio_file):
    """Transcribe audio using whisper.cpp"""
    try:
        whisper_cli = "/home/mla436/whisper.cpp/build/bin/whisper-cli"
        model_path = "/home/mla436/whisper.cpp/models/ggml-tiny.bin"
        
        transcriptions_dir = os.path.join(os.path.dirname(__file__), "transcriptions")
        os.makedirs(transcriptions_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_base = os.path.join(transcriptions_dir, f"transcription_{timestamp}")
        
        cmd = [
            whisper_cli,
            "-m", model_path,
            "-f", audio_file,
            "--output-txt",
            "--output-file", output_base,
            "-l", "en",
            "--no-timestamps"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            txt_file = f"{output_base}.txt"
            if os.path.exists(txt_file):
                with open(txt_file, 'r') as f:
                    transcription = f.read().strip()
                return transcription, txt_file
            else:
                st.session_state.error = "Transcription file not found"
                return None, None
        else:
            st.session_state.error = f"Whisper error: {result.stderr}"
            return None, None
    except Exception as e:
        st.session_state.error = f"Error transcribing audio: {e}"
        return None, None


def process_voice_input(audio_bytes):
    """Process voice input: save → convert → transcribe"""
    filepath, filename = save_audio_recording(audio_bytes)
    if not filepath:
        return None
    
    converted_file = convert_to_wav_16khz(filepath)
    if not converted_file:
        return None
    
    transcription, txt_file = transcribe_with_whisper(converted_file)
    return transcription


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

if "last_audio_url" not in st.session_state:
    st.session_state.last_audio_url = None

if "pending_audio" not in st.session_state:
    st.session_state.pending_audio = None


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
        r = requests.get(f"{api}/network-status", timeout=30)
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
        r = requests.get(f"{api}/ai-status", timeout=30)
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
        timeout=120
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


def component_ai_status(ai_data: Optional[Dict]):
    """Display AI brain status"""
    icon = "🧠"
    badge_color = {"good": "#4ade80", "warning": "#fbbf24", "error": "#f87171"}
    
    if not ai_data:
        st.markdown(f"""
        <div class="glass" style="padding:16px;margin-bottom:12px;">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
            <div style="width:40px;height:40px;border-radius:12px;background:rgba(255,255,255,0.10);
                 border:1px solid var(--border);display:flex;align-items:center;justify-content:center;">
              <div style="font-size:18px">{icon}</div>
            </div>
            <div style="flex:1"><div class="card-title">AI Brain Status</div></div>
            <span style="display:inline-block;width:10px;height:10px;border-radius:50%;
            background:{badge_color['error']};box-shadow:0 0 10px {badge_color['error']};"></span>
          </div>
          <div class="small" style="color:#fecaca">Unable to connect to AI brain</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    ai_model = ai_data.get('ai_model_loaded', False)
    rag_enabled = ai_data.get('rag_enabled', False)
    knowledge_size = ai_data.get('knowledge_base_size', 0)
    tts_available = ai_data.get('tts_available', False)
    
    dot_status = "good" if ai_model else "warning"
    dot_color = badge_color[dot_status]
    
    st.markdown(f"""
    <div class="glass" style="padding:16px;margin-bottom:12px;">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
        <div style="width:40px;height:40px;border-radius:12px;background:rgba(255,255,255,0.10);
             border:1px solid var(--border);display:flex;align-items:center;justify-content:center;">
          <div style="font-size:18px">{icon}</div>
        </div>
        <div style="flex:1"><div class="card-title">AI Brain Status</div></div>
        <span style="display:inline-block;width:10px;height:10px;border-radius:50%;
        background:{dot_color};box-shadow:0 0 10px {dot_color};"></span>
      </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**AI Model:**")
    with c2:
        st.markdown(f"{'distilgpt2' if ai_model else 'Rule-based'}")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**RAG Knowledge:**")
    with c2:
        st.markdown(f"{'Enabled' if rag_enabled else 'Disabled'}")
    
    if rag_enabled:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**KB Size:**")
        with c2:
            st.markdown(f"{knowledge_size} items")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**TTS (Piper):**")
    with c2:
        st.markdown(f"{'Available' if tts_available else 'N/A'}")
    
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
                st.markdown(f"""<div class="small" style="color:#fecaca">Audio unavailable: {audio_url}</div>""",
                          unsafe_allow_html=True)
        
        # Show AI analysis details in expandable section
        if role == "assistant":
            if ai_model_used or rag_enabled:
                with st.expander("🧠 AI Brain Analysis Details", expanded=False):
                    if ai_model_used:
                        st.write("**AI Model:** distilgpt2 (Used)")
                    if rag_enabled:
                        st.write("**RAG Knowledge:** Enabled")
                    if audio_url:
                        st.write("**Voice Response:** Available")


def component_chat_input(on_send, on_voice, is_processing: bool):
    # Voice input with audio recorder
    st.markdown('<div style="margin-bottom: 10px;">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 5])
    
    with col1:
        st.markdown("**🎤 Voice:**")
        audio_bytes = audio_recorder(
            text="",
            recording_color="#e74c3c",
            neutral_color="#3498db",
            icon_name="microphone",
            icon_size="2x",
            key="voice_input"
        )
        
        # Auto-process voice input when new recording detected
        if audio_bytes and audio_bytes != st.session_state.pending_audio:
            st.session_state.pending_audio = audio_bytes
            on_voice(audio_bytes)
            st.rerun()
    
    with col2:
        st.markdown("**💬 Text:**")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Text area with proper key management
    msg = st.text_area("",
                      value=st.session_state.chat_input_text,
                      key="chat_textarea",
                      placeholder="Ask the AI brain about your network...",
                      disabled=is_processing,
                      label_visibility="collapsed",
                      help="Type your message here",
                      height=110)
    
    c1, c2 = st.columns([2, 6])
    
    with c1:
        if st.button("📨 Send", 
                    disabled=is_processing or not msg.strip(),
                    use_container_width=True):
            on_send(msg)
            st.session_state.chat_input_text = ""
            st.rerun()
    
    st.markdown('<div class="small">Type your message and press Send • Use the microphone button above for voice input • Voice will auto-transcribe and send</div>',
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


def handle_voice_input(audio_bytes):
    """Process real voice input with Whisper transcription"""
    st.session_state.is_processing = True
    st.session_state.error = None
    
    try:
        # Process voice input (save, convert, transcribe)
        transcription = process_voice_input(audio_bytes)
        
        if transcription:
            # Send transcribed message to AI
            handle_send_message(transcription)
        else:
            st.session_state.error = "Failed to transcribe voice input. Please try again."
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
        component_ai_status(st.session_state.ai_data)
        component_suggestions(lambda s: handle_send_message(s))
    
    with right:
        # Chat panel
        st.markdown('<div class="glass" style="padding:18px;min-height:500px;max-height:500px;overflow-y:auto;">',
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
            st.markdown('<div class="small" style="text-align:center;padding:20px;">🧠 AI brain is analyzing your network...</div>', 
                       unsafe_allow_html=True)
        
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
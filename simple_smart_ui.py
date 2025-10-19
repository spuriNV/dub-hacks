#!/usr/bin/env python3
"""
Simple Smart AI Chatbot UI
Streamlit interface for the AI brain with glassmorphism design
"""

import streamlit as st
import requests
import json
import time
import os
import subprocess
from datetime import datetime
from audio_recorder_streamlit import audio_recorder

# Configure Streamlit page
st.set_page_config(
    page_title="AI Network Brain",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Glassmorphism + gradient CSS
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
  color: white;
}

.status-indicator {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 0.5rem;
}

.status-good { background-color: #4ade80; box-shadow: 0 0 10px #4ade80; }
.status-warning { background-color: #fbbf24; box-shadow: 0 0 10px #fbbf24; }
.status-error { background-color: #f87171; box-shadow: 0 0 10px #f87171; }

.small { font-size: 0.8rem; color: var(--muted); }

/* Sidebar styling */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(15,32,39,0.95) 0%, rgba(26,42,108,0.95) 100%) !important;
}

/* Chat message styling */
.stChatMessage {
  background: var(--panel) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  backdrop-filter: blur(18px);
}

/* Text input styling */
.stTextInput > div > div > input {
  background: rgba(255,255,255,0.05) !important;
  border: 1px solid var(--border) !important;
  color: white !important;
  border-radius: 8px !important;
}

/* Button styling */
.stButton > button {
  background: rgba(59,130,246,0.3) !important;
  border: 1px solid rgba(59,130,246,0.5) !important;
  color: white !important;
  border-radius: 8px !important;
  backdrop-filter: blur(10px);
}

.stButton > button:hover {
  background: rgba(59,130,246,0.5) !important;
  border: 1px solid rgba(59,130,246,0.7) !important;
}

/* Checkbox styling */
.stCheckbox > label {
  color: white !important;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_url" not in st.session_state:
    st.session_state.api_url = "http://localhost:8088"

if "voice_mode_enabled" not in st.session_state:
    st.session_state.voice_mode_enabled = False

if "last_audio_url" not in st.session_state:
    st.session_state.last_audio_url = None

if "pending_audio" not in st.session_state:
    st.session_state.pending_audio = None

def get_network_status():
    """Get current network status from AI brain"""
    try:
        response = requests.get(f"{st.session_state.api_url}/network-status", timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

def get_ai_status():
    """Get AI brain status"""
    try:
        response = requests.get(f"{st.session_state.api_url}/ai-status", timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

def send_chat_message(message, generate_audio=False):
    """Send message to AI brain and get response"""
    try:
        response = requests.post(
            f"{st.session_state.api_url}/chat",
            json={"message": message, "generate_audio": generate_audio},
            timeout=120
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error connecting to AI brain: {e}")
        return None

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
        st.error(f"Error saving recording: {e}")
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
            st.error(f"FFmpeg error: {result.stderr}")
            return None
    except Exception as e:
        st.error(f"Error converting audio: {e}")
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
                st.error("Transcription file not found")
                return None, None
        else:
            st.error(f"Whisper error: {result.stderr}")
            return None, None
    except Exception as e:
        st.error(f"Error transcribing audio: {e}")
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

def display_status_card(icon, title, content_html, dot_status=None):
    """Display a glassmorphism status card"""
    dot_html = ""
    if dot_status:
        dot_html = f'<span class="status-indicator status-{dot_status}"></span>'
    
    st.markdown(f"""
    <div class="glass" style="padding:16px;margin-bottom:12px;">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
        <div style="width:40px;height:40px;border-radius:12px;background:rgba(255,255,255,0.10);
             border:1px solid var(--border);display:flex;align-items:center;justify-content:center;">
          <div style="font-size:18px">{icon}</div>
        </div>
        <div style="flex:1"><div class="card-title">{title}</div></div>
        {dot_html}
      </div>
      {content_html}
    </div>
    """, unsafe_allow_html=True)

def display_network_status():
    """Display current network status in sidebar"""
    network_data = get_network_status()
    
    if not network_data:
        display_status_card("📶", "Network Status", 
                          '<p class="small" style="color:#fecaca">Unable to connect to AI brain</p>',
                          "error")
        return
    
    wifi = network_data.get('network_data', {}).get('wifi', {})
    connectivity = network_data.get('network_data', {}).get('connectivity', {})
    performance = network_data.get('network_data', {}).get('performance', {})
    
    # WiFi Status
    wifi_status = wifi.get('status', 'unknown')
    wifi_ssid = wifi.get('ssid', 'Unknown')
    signal_strength = wifi.get('signal_strength', 'unknown')
    
    if wifi_status == 'connected':
        wifi_content = f"""
        <p style="color:white;margin:4px 0;"><strong>Connected to:</strong> {wifi_ssid}</p>
        <p style="color:white;margin:4px 0;"><strong>Signal:</strong> {signal_strength} dBm</p>
        """
        display_status_card("📶", "WiFi Status", wifi_content, "good")
    else:
        display_status_card("📶", "WiFi Status", 
                          '<p class="small" style="color:#fecaca">Not Connected</p>',
                          "error")
    
    # Internet Status
    internet_connected = connectivity.get('internet_connected', False)
    latency = connectivity.get('latency', 'unknown')
    
    if internet_connected:
        internet_content = f"""
        <p style="color:white;margin:4px 0;"><strong>Status:</strong> Connected</p>
        <p style="color:white;margin:4px 0;"><strong>Latency:</strong> {latency}</p>
        """
        display_status_card("🌐", "Internet Status", internet_content, "good")
    else:
        display_status_card("🌐", "Internet Status",
                          '<p class="small" style="color:#fecaca">Not Connected</p>',
                          "error")
    
    # Performance Status
    quality = performance.get('network_quality', 'unknown')
    active_connections = performance.get('active_connections', 0)
    
    if quality in ("excellent", "good"):
        perf_status = "good"
    elif quality == "fair":
        perf_status = "warning"
    else:
        perf_status = "error"
    
    perf_content = f"""
    <p style="color:white;margin:4px 0;"><strong>Quality:</strong> {quality.title()}</p>
    <p style="color:white;margin:4px 0;"><strong>Active Connections:</strong> {active_connections}</p>
    """
    display_status_card("⚡", "Performance", perf_content, perf_status)

def display_ai_status():
    """Display AI brain status"""
    ai_status = get_ai_status()
    
    if not ai_status:
        display_status_card("🧠", "AI Brain Status",
                          '<p class="small" style="color:#fecaca">Unable to get AI brain status</p>',
                          "error")
        return
    
    ai_model = ai_status.get('ai_model_loaded', False)
    rag_enabled = ai_status.get('rag_enabled', False)
    knowledge_size = ai_status.get('knowledge_base_size', 0)
    tts_available = ai_status.get('tts_available', False)
    
    # AI Model
    if ai_model:
        model_content = '<p style="color:white;margin:4px 0;"><strong>distilgpt2 Loaded</strong></p>'
        display_status_card("🤖", "AI Model", model_content, "good")
    else:
        model_content = '<p style="color:white;margin:4px 0;"><strong>Rule-based Mode</strong></p>'
        display_status_card("🤖", "AI Model", model_content, "warning")
    
    # RAG Knowledge
    if rag_enabled:
        rag_content = f'<p style="color:white;margin:4px 0;"><strong>{knowledge_size} Items Loaded</strong></p>'
        display_status_card("📚", "RAG Knowledge", rag_content, "good")
    else:
        display_status_card("📚", "RAG Knowledge",
                          '<p class="small" style="color:#fecaca">Not Available</p>',
                          "error")
    
    # TTS Status
    if tts_available:
        tts_content = '<p style="color:white;margin:4px 0;"><strong>Piper Available</strong></p>'
        display_status_card("🔊", "Voice (TTS)", tts_content, "good")
    else:
        display_status_card("🔊", "Voice (TTS)",
                          '<p class="small" style="color:#fecaca">Not Available</p>',
                          "error")

def main():
    """Main application"""
    # Header
    st.markdown("""
    <div class="glass" style="padding:14px 18px;margin-bottom:18px;border-radius:16px;">
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

    # Sidebar
    with st.sidebar:
        st.markdown("### 🔧 Settings")
        api_url = st.text_input("API URL", value=st.session_state.api_url, 
                               help="URL of the AI brain API server")
        if api_url != st.session_state.api_url:
            st.session_state.api_url = api_url
            st.rerun()

        st.markdown("---")
        st.markdown("### 🎙️ Voice Mode")
        voice_mode = st.checkbox(
            "Enable Voice Responses",
            value=st.session_state.voice_mode_enabled,
            help="AI will speak responses using Piper TTS"
        )
        if voice_mode != st.session_state.voice_mode_enabled:
            st.session_state.voice_mode_enabled = voice_mode

        st.markdown("---")
        st.markdown("### 📊 Network Status")
        display_network_status()

        st.markdown("---")
        st.markdown("### 🤖 AI Brain Status")
        display_ai_status()

        st.markdown("---")
        st.markdown("""
        <div class="glass" style="padding:12px;background: linear-gradient(135deg, rgba(245,158,11,0.2), rgba(253,224,71,0.2));">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
            <span>💡</span><div class="card-title">Ask the AI Brain</div>
          </div>
          <div class="small">
            <p>• "What's wrong with my WiFi?"</p>
            <p>• "My internet is slow, help me"</p>
            <p>• "How can I improve my signal?"</p>
            <p>• "Check my network security"</p>
            <p>• "Why is my connection dropping?"</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # Chat interface
    st.markdown("### 💬 Chat with AI Brain")

    # Display chat messages
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show audio player for assistant messages if audio URL is stored
            if message["role"] == "assistant" and "audio_url" in message:
                st.audio(message["audio_url"], format="audio/wav")
            
            # Show AI analysis details for assistant messages
            if message["role"] == "assistant" and "ai_model_used" in message:
                with st.expander("🧠 AI Brain Analysis Details"):
                    st.write(f"**AI Model Used:** {'Yes (distilgpt2)' if message.get('ai_model_used') else 'No (rule-based)'}")
                    st.write(f"**RAG Knowledge:** {'Enabled' if message.get('rag_enabled') else 'Disabled'}")
                    st.write(f"**Voice Response:** {'Yes' if message.get('audio_url') else 'No'}")

    # Voice input section
    st.markdown("---")
    st.markdown("#### 🎤 Voice Input or Type Below")
    col_voice, col_text = st.columns([1, 5])

    with col_voice:
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

        with st.spinner("🎙️ Processing voice → Transcribing → Getting AI response..."):
            transcription = process_voice_input(audio_bytes)

            if transcription:
                # Add user message
                st.session_state.messages.append({"role": "user", "content": transcription})

                # Get AI response
                response = send_chat_message(transcription, 
                                           generate_audio=st.session_state.voice_mode_enabled)

                if response:
                    ai_response = response.get('response', 'Sorry, I could not process your request.')
                    audio_url = response.get('audio_url')
                    ai_model_used = response.get('ai_model_used', False)
                    rag_enabled = response.get('rag_enabled', False)

                    # Build message with all metadata
                    message_data = {
                        "role": "assistant", 
                        "content": ai_response,
                        "ai_model_used": ai_model_used,
                        "rag_enabled": rag_enabled
                    }
                    
                    if audio_url:
                        full_audio_url = f"{st.session_state.api_url}{audio_url}"
                        message_data["audio_url"] = full_audio_url
                        st.session_state.last_audio_url = full_audio_url

                    st.session_state.messages.append(message_data)
                    st.rerun()
                else:
                    st.error("❌ Failed to get AI response")
            else:
                st.error("❌ Voice transcription failed")

    # Chat input
    if prompt := st.chat_input("Ask the AI brain about your network..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI brain response
        with st.chat_message("assistant"):
            with st.spinner("🧠 AI brain is analyzing your network..."):
                response = send_chat_message(prompt, 
                                           generate_audio=st.session_state.voice_mode_enabled)

                if response:
                    ai_response = response.get('response', 'Sorry, I could not process your request.')
                    audio_url = response.get('audio_url')
                    ai_model_used = response.get('ai_model_used', False)
                    rag_enabled = response.get('rag_enabled', False)

                    st.markdown(ai_response)

                    # Play audio if available
                    if audio_url and st.session_state.voice_mode_enabled:
                        full_audio_url = f"{st.session_state.api_url}{audio_url}"
                        st.audio(full_audio_url, format="audio/wav", autoplay=True)

                    # Show AI brain analysis
                    with st.expander("🧠 AI Brain Analysis Details"):
                        st.write(f"**AI Model Used:** {'Yes (distilgpt2)' if ai_model_used else 'No (rule-based)'}")
                        st.write(f"**RAG Knowledge:** {'Enabled' if rag_enabled else 'Disabled'}")
                        st.write(f"**Voice Response:** {'Yes' if audio_url else 'No'}")
                        st.write(f"**Response Time:** {response.get('timestamp', 'Unknown')}")

                    # Add AI response to messages with all metadata
                    message_data = {
                        "role": "assistant", 
                        "content": ai_response,
                        "ai_model_used": ai_model_used,
                        "rag_enabled": rag_enabled
                    }
                    
                    if audio_url and st.session_state.voice_mode_enabled:
                        message_data["audio_url"] = f"{st.session_state.api_url}{audio_url}"
                    
                    st.session_state.messages.append(message_data)
                else:
                    st.error("❌ Failed to get response from AI brain. Please check if the API server is running.")

    # Footer
    st.markdown("""
    <div class="glass" style="padding:12px 16px;margin-top:18px;border-radius:16px;">
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;text-align:center;" class="small">
        <div><strong>AI Brain:</strong> RAG + distilgpt2</div>
        <div><strong>Analysis:</strong> Real-time CLI</div>
        <div><strong>Version:</strong> 8.0.0</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
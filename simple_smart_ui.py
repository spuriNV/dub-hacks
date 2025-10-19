#!/usr/bin/env python3
"""
Simple Smart AI Chatbot UI
Streamlit interface for the AI brain
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
    .voice-input-container {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
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
        response = requests.get(f"{st.session_state.api_url}/network-status", timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Network status error: {e}")
        return None

def get_ai_status():
    """Get AI brain status"""
    try:
        response = requests.get(f"{st.session_state.api_url}/ai-status", timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"AI status error: {e}")
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
        tts_available = ai_status.get('tts_available', False)

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

        # TTS Status
        if tts_available:
            st.sidebar.markdown(f"""
            <div class="ai-brain">
                <h4>🔊 Voice (TTS)</h4>
                <p><span class="status-indicator status-good"></span>Piper Available</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.sidebar.markdown(f"""
            <div class="ai-brain">
                <h4>🔊 Voice (TTS)</h4>
                <p><span class="status-indicator status-error"></span>Not Available</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.sidebar.error("❌ Unable to get AI brain status")

def save_audio_recording(audio_bytes):
    """Save audio recording to recordings folder"""
    try:
        # Create recordings folder if it doesn't exist
        recordings_dir = os.path.join(os.path.dirname(__file__), "recordings")
        os.makedirs(recordings_dir, exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.wav"
        filepath = os.path.join(recordings_dir, filename)

        # Save the audio file
        with open(filepath, "wb") as f:
            f.write(audio_bytes)

        return filepath, filename
    except Exception as e:
        st.error(f"Error saving recording: {e}")
        return None, None

def convert_to_wav_16khz(input_file):
    """Convert audio to 16kHz WAV format for whisper.cpp"""
    try:
        # Generate output filename
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_16khz.wav"

        # Use ffmpeg to convert
        cmd = [
            "ffmpeg",
            "-i", input_file,
            "-ar", "16000",  # 16kHz sample rate
            "-ac", "1",      # mono
            "-c:a", "pcm_s16le",  # 16-bit PCM
            "-y",            # overwrite output file
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
        # Paths
        whisper_cli = "/Users/sakethpoori/Documents/hacks/whisper.cpp/build/bin/whisper-cli"
        model_path = "/Users/sakethpoori/Documents/hacks/whisper.cpp/models/ggml-tiny.bin"

        # Create transcriptions folder
        transcriptions_dir = os.path.join(os.path.dirname(__file__), "transcriptions")
        os.makedirs(transcriptions_dir, exist_ok=True)

        # Generate output file path (without extension)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_base = os.path.join(transcriptions_dir, f"transcription_{timestamp}")

        # Run whisper.cpp
        cmd = [
            whisper_cli,
            "-m", model_path,
            "-f", audio_file,
            "--output-txt",           # Output text file
            "--output-file", output_base,
            "-l", "en",               # English language
            "--no-timestamps"         # Clean text without timestamps
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            # Read the generated text file
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
    """Process voice input automatically in background"""
    # Save recording
    filepath, filename = save_audio_recording(audio_bytes)

    if not filepath:
        return None

    # Convert to 16kHz WAV
    converted_file = convert_to_wav_16khz(filepath)

    if not converted_file:
        return None

    # Transcribe with Whisper
    transcription, txt_file = transcribe_with_whisper(converted_file)

    return transcription

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

        # Voice mode toggle
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
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # Show audio player for assistant messages if audio URL is stored
            if message["role"] == "assistant" and "audio_url" in message:
                st.audio(message["audio_url"], format="audio/wav")

    # Voice input section - positioned near chat input
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

        # Process voice in background with single spinner
        with st.spinner("🎙️ Processing voice → Transcribing → Getting AI response..."):
            transcription = process_voice_input(audio_bytes)

            if transcription:
                # Add user message
                st.session_state.messages.append({"role": "user", "content": transcription})

                # Get AI response
                response = send_chat_message(transcription, generate_audio=st.session_state.voice_mode_enabled)

                if response:
                    ai_response = response.get('response', 'Sorry, I could not process your request.')
                    audio_url = response.get('audio_url')

                    # Build message with audio URL if available
                    message_data = {"role": "assistant", "content": ai_response}
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
                response = send_chat_message(prompt, generate_audio=st.session_state.voice_mode_enabled)

                if response:
                    ai_response = response.get('response', 'Sorry, I could not process your request.')
                    audio_url = response.get('audio_url')

                    st.markdown(ai_response)

                    # Play audio if available
                    if audio_url and st.session_state.voice_mode_enabled:
                        full_audio_url = f"{st.session_state.api_url}{audio_url}"
                        st.audio(full_audio_url, format="audio/wav", autoplay=True)

                    # Show AI brain status
                    ai_model_used = response.get('ai_model_used', False)
                    rag_enabled = response.get('rag_enabled', False)

                    with st.expander("🧠 AI Brain Analysis Details"):
                        st.write(f"**AI Model Used:** {'Yes (distilgpt2)' if ai_model_used else 'No (rule-based)'}")
                        st.write(f"**RAG Knowledge:** {'Enabled' if rag_enabled else 'Disabled'}")
                        st.write(f"**Voice Response:** {'Yes' if audio_url else 'No'}")
                        st.write(f"**Response Time:** {response.get('timestamp', 'Unknown')}")

                    # Add AI response to messages with audio URL
                    message_data = {"role": "assistant", "content": ai_response}
                    if audio_url and st.session_state.voice_mode_enabled:
                        message_data["audio_url"] = f"{st.session_state.api_url}{audio_url}"
                    st.session_state.messages.append(message_data)
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
        st.markdown("**Version:** 8.0.0")

if __name__ == "__main__":
    main()

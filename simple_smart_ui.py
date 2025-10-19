#!/usr/bin/env python3
"""
Simple Smart AI Chatbot UI
Flask server that serves React frontend and proxies API requests to AI brain
"""

from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import requests
import os
import logging
import subprocess
from datetime import datetime
from werkzeug.utils import secure_filename
from piper_tts_module import get_piper_tts

# Configure Flask app
app = Flask(__name__, static_folder='frontend/build', static_url_path='')
CORS(app)  # Enable CORS for frontend

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AI Brain API configuration
AI_BRAIN_API_URL = os.getenv('AI_BRAIN_API_URL', 'http://localhost:8088')

# Initialize Piper TTS
logger.info("Initializing Piper TTS...")
piper_tts = get_piper_tts()
if piper_tts.piper_available:
    logger.info("✅ Piper TTS ready!")
else:
    logger.warning("⚠️  Piper TTS not available")

# Voice recording configuration
RECORDINGS_FOLDER = os.path.join(os.path.dirname(__file__), 'recordings')
REPLIES_FOLDER = os.path.join(os.path.dirname(__file__), 'replies')
AUDIO_FOLDER = os.path.join(os.path.dirname(__file__), 'audio')
ALLOWED_EXTENSIONS = {'wav', 'webm', 'mp3', 'ogg', 'm4a'}

# Create folders if they don't exist
os.makedirs(RECORDINGS_FOLDER, exist_ok=True)
os.makedirs(REPLIES_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_wav(input_file):
    """Convert audio to WAV format using ffmpeg"""
    try:
        # Generate output filename
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_16khz.wav"

        # Use ffmpeg to convert
        cmd = [
            'ffmpeg', '-i', input_file,
            '-ar', '16000',  # 16kHz sample rate
            '-ac', '1',      # mono
            '-c:a', 'pcm_s16le',  # 16-bit PCM
            '-y',  # overwrite output file
            output_file
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return output_file
        else:
            st.error(f"FFmpeg conversion failed: {result.stderr}")
            return None
    except Exception as e:
        st.error(f"Error converting audio: {e}")
        return None

def get_network_status():
    """Get current network status from AI brain"""
    try:
        # Add timestamp to prevent caching
        # Extended timeout to 30s for operations that take longer
        response = requests.get(
            f"{st.session_state.api_url}/network-status?t={int(time.time() * 1000)}",
            timeout=30,
            headers={'Cache-Control': 'no-cache'}
        )
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

    # Show last update time
    current_time = datetime.now().strftime("%H:%M:%S")
    st.sidebar.markdown(f"<small style='color: #888;'>Last updated: {current_time}</small>", unsafe_allow_html=True)

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
            'ffmpeg', '-i', input_file,
            '-ar', '16000',  # 16kHz sample rate
            '-ac', '1',      # mono
            '-c:a', 'pcm_s16le',  # 16-bit PCM
            '-y',            # overwrite
            output_file
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return output_file
        else:
            logger.error(f"FFmpeg error: {result.stderr}")
            return None
    except Exception as e:
        logger.error(f"Audio conversion error: {e}")
        return None

def transcribe_audio(audio_file):
    """
    Transcribe audio using Whisper.cpp or Web Speech API
    Replace this with actual Whisper implementation
    """
    try:
        # Check if Whisper.cpp is available
        whisper_cli = os.path.expanduser("~/whisper.cpp/build/bin/whisper-cli")
        model_path = os.path.expanduser("~/whisper.cpp/models/ggml-tiny.bin")
        
        if os.path.exists(whisper_cli) and os.path.exists(model_path):
            # Use Whisper.cpp
            output_base = audio_file.rsplit('.', 1)[0]
            cmd = [
                whisper_cli,
                '-m', model_path,
                '-f', audio_file,
                '--output-txt',
                '--output-file', output_base,
                '-l', 'en',
                '--no-timestamps'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                txt_file = f"{output_base}.txt"
                if os.path.exists(txt_file):
                    with open(txt_file, 'r') as f:
                        transcription = f.read().strip()
                    return transcription
        
        # Fallback: Return a message that transcription is pending
        logger.warning("Whisper not available, returning placeholder")
        return "[Whisper transcription pending - please set up Whisper.cpp or use Web Speech API]"
        
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return f"[Transcription error: {str(e)}]"

# Routes

@app.route('/')
def serve_frontend():
    """Serve the React frontend"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files from React build"""
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/network-status', methods=['GET'])
def network_status():
    """Proxy network status request to AI brain"""
    try:
        response = requests.get(
            f"{AI_BRAIN_API_URL}/network-status",
            timeout=5,
            headers={'Cache-Control': 'no-cache'}
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Network status error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/ai-status', methods=['GET'])
def ai_status():
    """Proxy AI status request to AI brain"""
    try:
        response = requests.get(f"{AI_BRAIN_API_URL}/ai-status", timeout=30)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"AI status error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Proxy chat request to AI brain and generate TTS if enabled"""
    try:
        data = request.get_json()
        generate_audio = data.get('generate_audio', False)
        
        logger.info(f"🗣️  Chat request received. TTS enabled: {generate_audio}")
        
        # Forward request to AI brain (without TTS, we'll handle that ourselves)
        ai_data = dict(data)
        ai_data['generate_audio'] = False  # Don't let AI brain generate audio
        
        response = requests.post(
            f"{AI_BRAIN_API_URL}/chat",
            json=ai_data,
            timeout=120
        )
        
        if response.ok:
            result = response.json()
            ai_response_text = result.get('response', '')
            
            logger.info(f"📝 AI Response received: {ai_response_text[:100]}...")
            
            # If TTS is enabled and we have a response
            if generate_audio and ai_response_text and piper_tts.piper_available:
                logger.info("🎵 TTS enabled - generating audio...")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # Save the reply text to replies folder
                reply_filename = f"reply_{timestamp}.txt"
                reply_filepath = os.path.join(REPLIES_FOLDER, reply_filename)
                with open(reply_filepath, 'w') as f:
                    f.write(ai_response_text)
                logger.info(f"✅ Saved reply text: {reply_filepath}")
                
                # Generate audio using Piper TTS
                audio_filename = f"reply_{timestamp}.wav"
                audio_filepath = os.path.join(AUDIO_FOLDER, audio_filename)
                
                logger.info(f"🔊 Generating TTS audio to: {audio_filepath}")
                success = piper_tts.text_to_speech(
                    text=ai_response_text,
                    output_file=audio_filepath,
                    max_length=500
                )
                
                if success:
                    logger.info(f"✅ Generated TTS audio: {audio_filepath}")
                    result['audio_url'] = f"/audio/{audio_filename}"
                else:
                    logger.error("❌ TTS generation failed")
            elif not generate_audio:
                logger.info("🔇 TTS disabled by user")
            elif not piper_tts.piper_available:
                logger.warning("⚠️  Piper TTS not available")
            elif not ai_response_text:
                logger.warning("⚠️  No response text to convert to speech")
            
            return jsonify(result), response.status_code
        else:
            logger.error(f"❌ AI Brain error: {response.status_code}")
            return jsonify(response.json()), response.status_code
            
    except Exception as e:
        logger.error(f"❌ Chat error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/voice', methods=['POST'])
def voice():
    """Handle voice input - save recording and transcribe"""
    try:
        # Check if audio file is in request
        if 'audio' not in request.files:
            return jsonify({
                "error": "No audio file provided",
                "success": False
            }), 400
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({
                "error": "No file selected",
                "success": False
            }), 400

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_extension = audio_file.filename.rsplit('.', 1)[1].lower() if '.' in audio_file.filename else 'webm'
        filename = f"recording_{timestamp}.{original_extension}"
        filepath = os.path.join(RECORDINGS_FOLDER, filename)
        
        # Save the original recording
        audio_file.save(filepath)
        logger.info(f"Saved recording: {filepath}")
        
        # Convert to WAV if needed
        if original_extension != 'wav':
            wav_file = convert_to_wav(filepath)
            if wav_file:
                filepath = wav_file
                logger.info(f"Converted to WAV: {wav_file}")
        
        # Transcribe the audio
        transcription = transcribe_audio(filepath)
        logger.info(f"Transcription: {transcription}")
        
        return jsonify({
            "transcription": transcription,
            "success": True,
            "filename": filename,
            "saved_path": filepath
        }), 200
        
    except Exception as e:
        logger.error(f"Voice error: {e}")
        return jsonify({
            "error": str(e),
            "success": False
        }), 500

# Serve audio files (locally generated by Piper TTS)
@app.route('/audio/<path:filename>')
def serve_audio(filename):
    """Serve audio files generated by Piper TTS"""
    try:
        audio_path = os.path.join(AUDIO_FOLDER, filename)
        if os.path.exists(audio_path):
            return send_from_directory(AUDIO_FOLDER, filename, mimetype='audio/wav')
        else:
            # Fallback: try to get from AI brain
            response = requests.get(f"{AI_BRAIN_API_URL}/audio/{filename}", stream=True)
            return response.content, response.status_code, {'Content-Type': 'audio/wav'}
    except Exception as e:
        logger.error(f"Audio error: {e}")
        return jsonify({"error": str(e)}), 500

def main():
    """Main application - Start Flask server"""
    logger.info("Starting AI Network Brain UI Server")
    logger.info(f"AI Brain API URL: {AI_BRAIN_API_URL}")
    logger.info("Frontend will be served from: frontend/build")
    logger.info("Server will run on: http://localhost:5002")

    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5002,
        debug=True,
        threaded=True
    )

if __name__ == "__main__":
    main()

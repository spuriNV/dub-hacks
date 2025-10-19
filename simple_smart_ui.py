#!/usr/bin/env python3
"""
Simple Smart AI Chatbot UI
Flask server to serve React frontend and handle API requests
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import requests
import json
import time
import os
import subprocess
from datetime import datetime
import threading

# Initialize Flask app
app = Flask(__name__, static_folder='frontend/build', static_url_path='')
CORS(app)

# AI Brain API URL
AI_API_URL = "http://localhost:8088"

def get_network_status():
    """Get current network status from AI brain"""
    try:
        response = requests.get(f"{AI_API_URL}/network-status", timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

def get_ai_status():
    """Get AI brain status"""
    try:
        response = requests.get(f"{AI_API_URL}/ai-status", timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

def send_chat_message(message, generate_audio=False):
    """Send message to AI brain and get response"""
    try:
        response = requests.post(
            f"{AI_API_URL}/chat",
            json={"message": message, "generate_audio": generate_audio},
            timeout=120
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error connecting to AI brain: {e}")
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
        print(f"Error saving recording: {e}")
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
            print(f"FFmpeg error: {result.stderr}")
            return None
    except Exception as e:
        print(f"Error converting audio: {e}")
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
                print("Transcription file not found")
                return None, None
        else:
            print(f"Whisper error: {result.stderr}")
            return None, None
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return None, None

def process_voice_input(audio_bytes):
    """Process voice input: save recording silently"""
    try:
        # Save the audio recording
        filepath, filename = save_audio_recording(audio_bytes)
        
        if not filepath:
            return None
            
        print(f"✅ Audio saved: {filename}")
        
        # Return success without message (frontend handles transcription)
        return "success"
        
    except Exception as e:
        print(f"Error processing voice input: {e}")
        return None
    
# API Routes
@app.route('/api/network-status')
def api_network_status():
    """API endpoint for network status"""
    try:
        network_data = get_network_status()
        if network_data:
            return jsonify(network_data)
        else:
            return jsonify({"error": "Unable to connect to AI brain"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ai-status')
def api_ai_status():
    """API endpoint for AI status"""
    try:
        ai_data = get_ai_status()
        if ai_data:
            return jsonify(ai_data)
        else:
            return jsonify({"error": "Unable to get AI brain status"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """API endpoint for chat messages"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        generate_audio = data.get('generate_audio', False)
        
        if not message:
            return jsonify({"error": "No message provided"}), 400
        
        # Send to AI brain
        response = send_chat_message(message, generate_audio)
        
        if response:
            return jsonify(response)
        else:
            return jsonify({"error": "Failed to get response from AI brain"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/voice', methods=['POST'])
def api_voice():
    """API endpoint for voice input"""
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files['audio']
        audio_bytes = audio_file.read()
        
        # Process voice input
        transcription = process_voice_input(audio_bytes)

        if transcription:
            return jsonify({"transcription": transcription})
        else:
            return jsonify({"error": "Failed to transcribe audio"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Serve React app
@app.route('/')
def serve_react_app():
    """Serve the React app"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    """Serve static files for React app"""
    return send_from_directory(app.static_folder, path)

# Health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": time.time()})

if __name__ == "__main__":
    print("🤖 Starting AI Network Brain Web Server...")
    print("=" * 50)
    print("🌐 React Frontend: http://localhost:5001")
    print("🧠 AI Brain API: http://localhost:8088")
    print("=" * 50)
    
    # Check if React build exists
    if not os.path.exists('frontend/build'):
        print("⚠️  React build not found. Please run 'npm run build' in the frontend directory.")
        print("   For development, you can run 'npm start' in the frontend directory instead.")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
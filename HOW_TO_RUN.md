# AI Brain Network Assistant - Setup Guide

A conversational AI assistant that analyzes your network in real-time and provides intelligent WiFi troubleshooting advice using RAG (Retrieval-Augmented Generation) and lightweight AI models.

## 🧠 What It Does

- **Real-time Network Analysis**: Uses CLI commands to check your actual WiFi/internet status
- **RAG Knowledge Retrieval**: Finds relevant troubleshooting info from professional sources
- **AI-Powered Responses**: Uses distilgpt2 model for intelligent, conversational answers
- **🎙️ Voice Communication**: Talk to your AI assistant using Whisper.cpp + Piper TTS (NEW!)
- **Cross-Platform**: Works on Mac, Linux, and Raspberry Pi
- **Offline**: No internet required - runs completely locally

## 🎙️ NEW: Voice Integration

Your AI Brain now supports **two-way voice communication**:
- **Speak** your questions using the microphone
- **Listen** to AI responses in natural speech
- **Offline** voice processing (Whisper.cpp + Piper TTS)

**Quick Voice Setup**: See [QUICKSTART_VOICE.md](QUICKSTART_VOICE.md) for a 5-minute setup guide!

## 📋 Prerequisites

- **Python 3.11+** (recommended)
- **macOS, Linux, or Raspberry Pi OS**
- **4GB+ RAM** (for AI model)
- **Terminal/Command Line access**

## 🚀 Quick Start

### 1. Clone/Download the Project
```bash
# If you have the files, navigate to the directory
cd /path/to/slm
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv_ai

# Activate virtual environment
# On macOS/Linux:
source venv_ai/bin/activate

# On Windows:
# venv_ai\Scripts\activate
```

### 3. Install Dependencies
```bash
# Install all required packages with one command
pip install -r requirements.txt
```

**📝 Note**: AI models are downloaded automatically on first run (this may take a few minutes).

**📋 Quick Reference**: See `installations.txt` for detailed commands and system-specific instructions.

### 4. Start the AI Brain
```bash
# Terminal 1: Start the API server
source venv_ai/bin/activate
python simple_smart_api.py

# Terminal 2: Start the chatbot UI
source venv_ai/bin/activate
streamlit run simple_smart_ui.py --server.port 8502 --server.headless true
```

### 5. Access the AI Brain
- **Chatbot UI**: http://localhost:8502
- **API Server**: http://localhost:8088
- **API Docs**: http://localhost:8088/docs

## 🔧 Detailed Setup

### System Requirements

#### macOS
- **Python**: 3.11+ (install via Homebrew: `brew install python`)
- **Dependencies**: All handled by pip
- **Network Commands**: Uses `networksetup`, `system_profiler`, `ifconfig`

#### Linux/Raspberry Pi
- **Python**: 3.11+ (`sudo apt install python3.11 python3.11-venv`)
- **Network Tools**: `sudo apt install wireless-tools iwconfig`
- **Dependencies**: All handled by pip

### Installation Steps

#### Step 1: Python Environment
```bash
# Check Python version
python --version  # Should be 3.11+

# Create virtual environment
python -m venv venv_ai
source venv_ai/bin/activate  # On Windows: venv_ai\Scripts\activate
```

#### Step 2: Install AI Dependencies
```bash
# Option 1: Install all at once (recommended)
pip install -r requirements.txt

# Option 2: Install individually (see installations.txt for details)
pip install transformers torch accelerate bitsandbytes scikit-learn
pip install fastapi uvicorn
pip install streamlit
pip install psutil requests
```

**📝 Note**: AI models (~1-2GB) are downloaded automatically on first run. This may take 5-10 minutes depending on your internet speed.

**📋 For detailed installation commands, system-specific instructions, and troubleshooting, see `installations.txt`**

#### Step 3: Download AI Models (First Run Only)
```bash
# Models are downloaded automatically on first run
# This may take 5-10 minutes and requires ~1-2GB of space
python simple_smart_ai.py
```

#### Step 4: Verify Installation
```bash
# Test the AI brain (models should be cached after first run)
python simple_smart_ai.py
```

## 🎯 Usage

### Starting the System

#### Method 1: Manual Start
```bash
# Terminal 1: API Server
source venv_ai/bin/activate
python simple_smart_api.py

# Terminal 2: Chatbot UI
source venv_ai/bin/activate
streamlit run simple_smart_ui.py --server.port 8502
```

#### Method 2: Background Start
```bash
# Start API server in background
source venv_ai/bin/activate
python simple_smart_api.py &

# Start UI in background
source venv_ai/bin/activate
streamlit run simple_smart_ui.py --server.port 8502 --server.headless true &
```

### Using the AI Brain

1. **Open Browser**: Go to http://localhost:8502
2. **Ask Questions**: Type questions about your network
3. **Get Responses**: AI analyzes your network and responds intelligently

#### Example Questions:
- "What's my WiFi status?"
- "My internet is slow, help me"
- "How can I improve my signal?"
- "What's wrong with my network?"
- "Check my network security"

## 🧠 How It Works

### AI Brain Components

1. **Network Analysis** (`simple_smart_ai.py`)
   - Runs CLI commands to check WiFi/internet status
   - Analyzes signal strength, latency, connectivity
   - Cross-platform support (Mac/Linux/Pi)

2. **RAG System** (Retrieval-Augmented Generation)
   - 4 comprehensive WiFi troubleshooting knowledge categories
   - Semantic search to find relevant solutions
   - Professional sources (IEEE standards, WiFi Alliance)

3. **AI Model** (distilgpt2)
   - Lightweight transformer model (~82MB)
   - Generates conversational responses
   - Fallback to rule-based responses

4. **API Server** (`simple_smart_api.py`)
   - FastAPI server on port 8088
   - RESTful endpoints for chat and network status
   - CORS enabled for web interface

5. **Chatbot UI** (`simple_smart_ui.py`)
   - Streamlit web interface on port 8502
   - Real-time network status in sidebar
   - Beautiful chat interface

### Response Flow

```
User Question → Network Analysis → RAG Knowledge Retrieval → AI Model → Conversational Response
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Kill existing processes
pkill -f simple_smart_api
pkill -f streamlit
lsof -ti:8088,8502 | xargs kill -9 2>/dev/null || true
```

#### 2. AI Model Loading Issues
```bash
# Check if model is loading
curl -s http://localhost:8088/ai-status

# If model fails, system falls back to rule-based responses
```

#### 3. Network Detection Issues
```bash
# Test network detection
python -c "from simple_smart_ai import SimpleSmartAI; ai = SimpleSmartAI(); print(ai.get_network_data())"
```

#### 4. Permission Issues (Linux/Pi)
```bash
# Install network tools
sudo apt install wireless-tools iwconfig

# Check WiFi interface
iwconfig
```

### Performance Optimization

#### For Raspberry Pi (4GB RAM)
```bash
# Use lighter model settings
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# Monitor memory usage
htop
```

#### For Better Performance
```bash
# Install watchdog for faster file changes
pip install watchdog

# Use SSD storage for model loading
```

## 📁 File Structure

```
dub-hacks/
├── simple_smart_ai.py           # AI brain (RAG + distilgpt2)
├── simple_smart_api.py          # FastAPI server
├── simple_smart_ui.py           # Streamlit chatbot UI
├── piper_tts_module.py          # Piper TTS integration (NEW)
│
├── requirements.txt             # Dependencies
├── venv_ai/                     # Virtual environment
│
├── recordings/                  # Voice recordings (NEW)
├── transcriptions/              # Whisper transcriptions (NEW)
├── audio_responses/             # TTS audio files (NEW)
│
├── HOW_TO_RUN.md               # This comprehensive guide
├── QUICKSTART_VOICE.md         # 5-minute voice setup (NEW)
├── VOICE_INTEGRATION_GUIDE.md  # Detailed voice guide (NEW)
├── VOICE_INTEGRATION_SUMMARY.md # Implementation summary (NEW)
│
├── setup_voice.sh              # Voice setup script (NEW)
├── test_voice_system.py        # Voice system test (NEW)
└── installations.txt           # Quick installation commands
```

### 📋 Quick Reference Files
- **`HOW_TO_RUN.md`**: Complete setup and usage guide (this file)
- **`QUICKSTART_VOICE.md`**: 5-minute voice setup guide
- **`VOICE_INTEGRATION_GUIDE.md`**: Detailed voice documentation
- **`installations.txt`**: Copy-paste installation commands
- **`simple_smart_ai.py`**: Core AI brain with RAG + model
- **`simple_smart_api.py`**: API server (port 8088)
- **`simple_smart_ui.py`**: Chatbot UI (port 8502)
- **`piper_tts_module.py`**: Piper TTS integration module

## 🚀 Deployment

### Local Development
- **API**: http://localhost:8088
- **UI**: http://localhost:8502
- **Docs**: http://localhost:8088/docs

### Production Deployment
- **Pi + Computer**: Run AI brain on Pi, access UI from computer
- **Docker**: Containerize for easy deployment
- **Systemd**: Run as service on Linux/Pi

### Raspberry Pi Setup
```bash
# Install dependencies
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
sudo apt install wireless-tools iwconfig

# Follow setup steps above
```

## 🎯 Features

### ✅ What Works
- **Real-time network analysis**
- **Conversational AI responses**
- **RAG knowledge retrieval**
- **🎙️ Voice input** (Whisper.cpp speech-to-text) - NEW!
- **🔊 Voice output** (Piper TTS text-to-speech) - NEW!
- **Voice conversations** (seamless voice-to-voice flow) - NEW!
- **Cross-platform support**
- **Offline operation**
- **Beautiful web interface**

### 🎙️ Voice Features (NEW)
- **Microphone recording** in browser
- **Automatic transcription** using Whisper.cpp
- **Natural voice responses** using Piper TTS
- **One-click voice chat** button
- **Toggle voice mode** on/off
- **Dual input modes**: voice OR text

### 🔮 Future Enhancements
- **More AI models** (Llama, Mistral)
- **Advanced network diagnostics**
- **Network optimization suggestions**
- **Historical network data**
- **Mobile app interface**
- **Multiple voice models** and languages

## 📞 Support

### Getting Help
1. **Check logs**: Look at terminal output for errors
2. **Test components**: Run individual components separately
3. **Check dependencies**: Ensure all packages are installed
4. **Network permissions**: Verify network access on your system

### Common Commands
```bash
# Check if API is running
curl -s http://localhost:8088/health

# Test chat endpoint
curl -X POST http://localhost:8088/chat -H "Content-Type: application/json" -d '{"message": "What is my WiFi status?"}'

# Check network data
curl -s http://localhost:8088/network-status
```

### 📋 Quick Commands Reference
For a complete list of installation, verification, and troubleshooting commands, see `installations.txt`.

---

**Your AI Brain is ready to intelligently analyze and troubleshoot your network!** 🤖✨

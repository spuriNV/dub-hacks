#!/bin/bash
# Setup Voice Integration for AI Network Brain
# Installs Piper TTS and verifies all components

set -e  # Exit on error

echo "======================================"
echo "AI Network Brain - Voice Setup"
echo "======================================"
echo ""

# Check if we're in the right directory
if [ ! -f "simple_smart_ai.py" ]; then
    echo "❌ Error: Please run this script from the dub-hacks directory"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
if [ ! -d "venv_ai" ]; then
    echo "❌ Error: venv_ai not found. Please create it first:"
    echo "   python -m venv venv_ai"
    exit 1
fi

source venv_ai/bin/activate

# Install Piper TTS
echo ""
echo "🔊 Installing Piper TTS..."
pip install piper-tts

# Verify installation
echo ""
echo "✅ Verifying Piper installation..."
if command -v piper &> /dev/null; then
    echo "✅ Piper TTS installed successfully!"
    piper --version
else
    echo "❌ Piper installation failed"
    exit 1
fi

# Check for Piper model
echo ""
echo "📥 Checking for Piper voice model..."
MODEL_DIR="$HOME/piper-tts-workflow/models"
MODEL_FILE="$MODEL_DIR/en_US-lessac-medium.onnx"
CONFIG_FILE="$MODEL_DIR/en_US-lessac-medium.onnx.json"

if [ -f "$MODEL_FILE" ] && [ -f "$CONFIG_FILE" ]; then
    echo "✅ Piper voice model already exists: $MODEL_FILE"
else
    echo "📥 Downloading Piper voice model..."
    mkdir -p "$MODEL_DIR"
    cd "$MODEL_DIR"

    echo "   Downloading model file..."
    wget -q --show-progress https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx

    echo "   Downloading config file..."
    wget -q --show-progress https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json

    cd - > /dev/null

    if [ -f "$MODEL_FILE" ] && [ -f "$CONFIG_FILE" ]; then
        echo "✅ Voice model downloaded successfully!"
    else
        echo "❌ Failed to download voice model"
        exit 1
    fi
fi

# Test Piper TTS
echo ""
echo "🧪 Testing Piper TTS..."
TEST_TEXT="Hello! This is a test of the voice system."
TEST_OUTPUT="/tmp/piper_test.wav"

echo "$TEST_TEXT" | piper --model "$MODEL_FILE" --output_file "$TEST_OUTPUT"

if [ -f "$TEST_OUTPUT" ]; then
    echo "✅ Piper TTS test successful!"
    echo "   Test audio saved to: $TEST_OUTPUT"
    echo "   Play with: ffplay -nodisp -autoexit $TEST_OUTPUT"
else
    echo "❌ Piper TTS test failed"
    exit 1
fi

# Run comprehensive test
echo ""
echo "🧪 Running comprehensive voice system test..."
cd /home/mla436/dub-hacks
python3 test_voice_system.py

echo ""
echo "======================================"
echo "✅ Voice Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "  1. Start API server:"
echo "     python simple_smart_api.py"
echo ""
echo "  2. In another terminal, start UI:"
echo "     streamlit run simple_smart_ui.py --server.port 8502"
echo ""
echo "  3. Open browser: http://localhost:8502"
echo "  4. Enable 'Voice Responses' in sidebar"
echo "  5. Try voice chat!"
echo ""

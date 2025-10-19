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

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

# Install Piper TTS
echo ""
echo "🔊 Installing Piper TTS..."
pip3 install piper-tts

# Verify installation
echo ""
echo "✅ Verifying Piper installation..."
if command -v piper &> /dev/null; then
    echo "✅ Piper TTS installed successfully!"
    piper --version
else
    echo "⚠️  Piper command not found in PATH, but package may be installed"
    echo "   You can use: python3 -m piper"
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
    if command -v wget &> /dev/null; then
        wget -q --show-progress https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
        wget -q --show-progress https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
    elif command -v curl &> /dev/null; then
        curl -L -o en_US-lessac-medium.onnx https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
        curl -L -o en_US-lessac-medium.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
    else
        echo "❌ Error: Neither wget nor curl is available"
        exit 1
    fi

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

if command -v piper &> /dev/null; then
    echo "$TEST_TEXT" | piper --model "$MODEL_FILE" --output_file "$TEST_OUTPUT"
else
    echo "$TEST_TEXT" | python3 -m piper --model "$MODEL_FILE" --output_file "$TEST_OUTPUT"
fi

if [ -f "$TEST_OUTPUT" ]; then
    echo "✅ Piper TTS test successful!"
    echo "   Test audio saved to: $TEST_OUTPUT"
    if command -v afplay &> /dev/null; then
        echo "   Playing test audio..."
        afplay "$TEST_OUTPUT"
    elif command -v ffplay &> /dev/null; then
        echo "   Play with: ffplay -nodisp -autoexit $TEST_OUTPUT"
    else
        echo "   Audio file created but no player found"
    fi
else
    echo "❌ Piper TTS test failed"
    exit 1
fi

echo ""
echo "======================================"
echo "✅ Voice Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "  1. Voice system is ready!"
echo "  2. Server is running on: http://localhost:5001"
echo "  3. Enable 'Voice Responses' in the web app"
echo "  4. Try voice chat with the microphone button!"
echo ""



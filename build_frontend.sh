#!/bin/bash
# Build script for React frontend

echo "🚀 Building AI Network Brain Frontend..."

# Navigate to frontend directory
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    npm install
fi

# Build the React app
echo "🔨 Building React app..."
npm run build

# Check if build was successful
if [ -d "build" ]; then
    echo "✅ Frontend built successfully!"
    echo "📁 Build output: frontend/build/"
    echo ""
    echo "Now you can run: python3 simple_smart_ui.py"
else
    echo "❌ Build failed!"
    exit 1
fi


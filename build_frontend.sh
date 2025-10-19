#!/bin/bash

echo "🔨 Building React Frontend for AI Network Brain..."
echo "=" * 50

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

# Navigate to frontend directory
cd frontend

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build the React app
echo "🔨 Building React app..."
npm run build

# Check if build was successful
if [ -d "build" ]; then
    echo "✅ React frontend built successfully!"
    echo "📁 Build files are in: frontend/build/"
else
    echo "❌ Build failed. Please check the error messages above."
    exit 1
fi

echo "🎉 Frontend build complete!"
echo "🚀 You can now run the Python server with: python simple_smart_ui.py"


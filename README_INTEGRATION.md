# AI Network Brain - React + Python Integration

This project integrates a React frontend with your Python AI backend to create a modern web application for network troubleshooting.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React App     │    │  Flask Server   │    │  AI Backend     │
│   (Frontend)    │◄──►│  (simple_ui.py) │◄──►│  (simple_ai.py) │
│   Port: 3000    │    │   Port: 5000    │    │   Port: 8088     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
dub-hacks/
├── simple_smart_ai.py          # AI Backend (unchanged)
├── simple_smart_api.py         # API Server (unchanged)
├── simple_smart_ui.py          # Flask Server (modified)
├── frontend/                   # React App
│   ├── src/
│   │   ├── components/         # React Components
│   │   │   ├── chat/           # Chat components
│   │   │   ├── status/         # Status components
│   │   │   ├── settings/       # Settings components
│   │   │   ├── suggestions/    # Suggestion components
│   │   │   └── ui/             # UI components
│   │   ├── pages/              # Pages
│   │   └── App.js             # Main App
│   ├── public/
│   ├── package.json
│   └── tailwind.config.js
├── requirements.txt            # Python dependencies
├── requirements_web.txt        # Flask dependencies
└── build_frontend.sh          # Build script
```

## 🚀 Quick Start

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
pip install -r requirements_web.txt
```

### 2. Build React Frontend
```bash
./build_frontend.sh
```

### 3. Start the AI Backend
```bash
python simple_smart_ai.py
```

### 4. Start the Flask Server
```bash
python simple_smart_ui.py
```

### 5. Access the Application
- **Web App**: http://localhost:5000
- **AI Backend**: http://localhost:8088

## 🛠️ Development Mode

For development with hot reload:

### 1. Start AI Backend
```bash
python simple_smart_ai.py
```

### 2. Start Flask Server (Terminal 1)
```bash
python simple_smart_ui.py
```

### 3. Start React Dev Server (Terminal 2)
```bash
cd frontend
npm start
```

Then access: http://localhost:3000

## 📋 React Components

### Chat Components
- **MessageBubble**: Displays chat messages with AI analysis details
- **ChatInput**: Text and voice input with recording capabilities

### Status Components
- **NetworkStatus**: WiFi connection status and signal strength
- **InternetStatus**: Internet connectivity and latency
- **PerformanceStatus**: Network quality and active connections
- **StatusCard**: Reusable status display component

### Settings Components
- **SettingsPanel**: API URL and voice mode configuration

### Suggestion Components
- **SuggestionsList**: Quick suggestion buttons for common questions

### UI Components
- **Button**: Styled button component
- **Input**: Form input component
- **Textarea**: Multi-line text input
- **Switch**: Toggle switch component
- **Alert**: Alert/notification component
- **Collapsible**: Expandable content component

## 🔧 API Endpoints

The Flask server provides these API endpoints:

- `GET /api/network-status` - Get current network status
- `GET /api/ai-status` - Get AI brain status
- `POST /api/chat` - Send chat message to AI brain
- `POST /api/voice` - Process voice input
- `GET /health` - Health check

## 🎨 Styling

The app uses:
- **Tailwind CSS** for utility-first styling
- **Framer Motion** for animations
- **Lucide React** for icons
- **Glassmorphism** design with backdrop blur effects
- **Gradient backgrounds** with animated elements

## 🔄 Data Flow

1. **User Input** → React Component
2. **API Call** → Flask Server (`/api/chat`)
3. **AI Processing** → Python Backend (`simple_smart_ai.py`)
4. **Response** → Flask Server
5. **Update UI** → React Component

## 🐛 Troubleshooting

### React Build Issues
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Python Dependencies
```bash
pip install --upgrade -r requirements.txt
pip install --upgrade -r requirements_web.txt
```

### Port Conflicts
- React Dev Server: 3000
- Flask Server: 5000
- AI Backend: 8088

Change ports in respective configuration files if needed.

## 📱 Features

### ✅ Implemented
- Modern React frontend with 12 components
- Flask API server integration
- Real-time network status monitoring
- Chat interface with AI responses
- Voice input simulation
- Settings management
- Responsive design
- Glassmorphism UI
- Status indicators
- Suggestion system

### 🔄 Integration Points
- All React components communicate with Python backend
- Flask server handles API routing
- Maintains AI Network Brain context
- Preserves all original functionality
- Adds modern web interface

## 🎯 Next Steps

1. **Test the integration** by running all components
2. **Customize styling** if needed
3. **Add more features** to React components
4. **Deploy** to production if desired

The integration is complete and ready to use! 🎉


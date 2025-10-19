import React, { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Loader2, AlertCircle, Brain } from "lucide-react";
import { Alert, AlertDescription } from "../components/ui/Alert";
import MessageBubble from "../components/chat/MessageBubble";
import ChatInput from "../components/chat/ChatInput";
import NetworkStatus from "../components/status/NetworkStatus";
import InternetStatus from "../components/status/InternetStatus";
import PerformanceStatus from "../components/status/PerformanceStatus";
import SettingsPanel from "../components/settings/SettingsPanel";
import SuggestionsList from "../components/suggestions/SuggestionsList";

export default function Dashboard() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [settings, setSettings] = useState({
    api_url: "http://localhost:8088",
    voice_mode_enabled: false
  });
  const [networkData, setNetworkData] = useState(null);
  const [aiData, setAiData] = useState(null);
  const [messages, setMessages] = useState([]);
  const messagesEndRef = React.useRef(null);

  const queryClient = useQueryClient();

  // Auto-scroll to bottom when new messages are added
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  React.useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load chat messages from localStorage
  useEffect(() => {
    // Clear old messages for fresh start
    localStorage.removeItem('ai-network-brain-messages');
    setMessages([]);
  }, []);

  // Save messages to localStorage
  useEffect(() => {
    localStorage.setItem('ai-network-brain-messages', JSON.stringify(messages));
  }, [messages]);

  // Fetch network status
  const fetchNetworkStatus = async () => {
    try {
      const response = await fetch(`${settings.api_url}/network-status`);
      if (response.ok) {
        const data = await response.json();
        setNetworkData(data.network_data);
      }
    } catch (err) {
      console.error("Network status error:", err);
    }
  };

  // Fetch AI status
  const fetchAIStatus = async () => {
    try {
      const response = await fetch(`${settings.api_url}/ai-status`);
      if (response.ok) {
        const data = await response.json();
        setAiData(data);
      }
    } catch (err) {
      console.error("AI status error:", err);
    }
  };

  // Load statuses periodically
  useEffect(() => {
    if (settings.api_url) {
      fetchNetworkStatus();
      fetchAIStatus();
      
      const interval = setInterval(() => {
        fetchNetworkStatus();
        fetchAIStatus();
      }, 10000); // Refresh every 10 seconds

      return () => clearInterval(interval);
    }
  }, [settings.api_url]);

  const handleSendMessage = async (content) => {
    setIsProcessing(true);
    setError(null);

    try {
      // Add user message
      const userMessage = {
        id: Date.now(),
        role: "user",
        content: content,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, userMessage]);

      // Send to AI brain
      const response = await fetch(`${settings.api_url}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: content,
          generate_audio: settings.voice_mode_enabled
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        // Add AI response
        const aiMessage = {
          id: Date.now() + 1,
          role: "assistant",
          content: data.response || "Sorry, I could not process your request.",
          audio_url: data.audio_url ? `${settings.api_url}${data.audio_url}` : undefined,
          ai_model_used: data.ai_model_used || false,
          rag_enabled: data.rag_enabled || false,
          timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        throw new Error("Failed to get AI response");
      }
    } catch (err) {
      console.error("Error:", err);
      setError("Failed to communicate with AI brain. Please check if the API server is running.");
      
      // Add error message
      const errorMessage = {
        id: Date.now(),
        role: "assistant",
        content: "Sorry, I'm having trouble connecting right now. Please try again later.",
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleVoiceInput = async (audioBlob, recognition) => {
    setIsProcessing(true);
    setError(null);

    try {
      // Save the audio recording to backend
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');
      
      // Save audio in background (don't wait for it)
      fetch('/api/voice', {
        method: 'POST',
        body: formData
      }).catch(err => console.error("Audio save error:", err));
      
      // Get transcript from the speech recognition
      if (recognition && recognition.transcript) {
        const transcript = recognition.transcript.trim();
        if (transcript) {
          // Send transcribed text to AI for response
          await handleSendMessage(transcript);
        } else {
          setError("No speech detected. Please try again.");
        }
      } else {
        setError("Speech recognition not available. Please use Chrome or Edge.");
      }
    } catch (err) {
      console.error("Voice input error:", err);
      setError("Failed to process voice input. Please try again.");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleUpdateSettings = (newSettings) => {
    setSettings(newSettings);
    localStorage.setItem('ai-network-brain-settings', JSON.stringify(newSettings));
  };

  // Load settings from localStorage
  useEffect(() => {
    const savedSettings = localStorage.getItem('ai-network-brain-settings');
    if (savedSettings) {
      setSettings(JSON.parse(savedSettings));
    }
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="grid lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1 space-y-6">
          <SettingsPanel 
            settings={settings}
            onUpdateSettings={handleUpdateSettings}
          />
          
          <NetworkStatus networkData={networkData} />
          
          <InternetStatus networkData={networkData} />
          
          <PerformanceStatus networkData={networkData} />
          
          <SuggestionsList onSelectSuggestion={handleSendMessage} />
        </div>

        {/* Main Chat Area */}
        <div className="lg:col-span-3">
          <div 
            className="backdrop-blur-xl bg-white/10 border border-white/20 rounded-2xl p-6 mb-6"
            style={{
              boxShadow: "0 8px 32px 0 rgba(31, 38, 135, 0.37)",
              minHeight: "600px",
              maxHeight: "600px",
              overflow: "hidden",
              display: "flex",
              flexDirection: "column"
            }}
          >
            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto mb-6 pr-2 space-y-4"
              style={{
                scrollbarWidth: "thin",
                scrollbarColor: "rgba(255, 255, 255, 0.3) transparent"
              }}
              ref={messagesEndRef}
            >
              {messages.length === 0 ? (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <div className="w-20 h-20 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-blue-500/30 to-indigo-500/30 flex items-center justify-center backdrop-blur-xl border border-white/20">
                      <Brain className="w-10 h-10 text-white" />
                    </div>
                    <h3 className="text-xl font-semibold text-white mb-2">
                      Welcome to AI Network Brain
                    </h3>
                    <p className="text-blue-200 mb-4">
                      Ask me anything about your network!
                    </p>
                  </div>
                </div>
              ) : (
                messages.map((message, index) => (
                  <MessageBubble key={message.id} message={message} index={index} />
                ))
              )}
              
              {isProcessing && (
                <div className="flex items-center gap-3 mb-4">
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center backdrop-blur-xl border border-white/20">
                    <Brain className="w-5 h-5 text-white" />
                  </div>
                  <div className="backdrop-blur-xl bg-white/10 border border-white/20 rounded-2xl px-4 py-3">
                    <div className="flex items-center gap-2">
                      <Loader2 className="w-4 h-4 text-white animate-spin" />
                      <span className="text-white text-sm">AI brain is analyzing...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Error Display */}
            {error && (
              <Alert variant="destructive" className="mb-4 backdrop-blur-xl bg-red-500/20 border-red-500/50">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Chat Input */}
            <ChatInput
              onSendMessage={handleSendMessage}
              onVoiceInput={handleVoiceInput}
              isProcessing={isProcessing}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

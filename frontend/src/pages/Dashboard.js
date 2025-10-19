import React, { useState, useEffect } from "react";
import { base44 } from "../api/base44Client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Loader2, AlertCircle } from "lucide-react";
import { Alert, AlertDescription } from "../components/ui/alert";
import MessageBubble from "../components/chat/MessageBubble";
import ChatInput from "../components/chat/ChatInput";
import NetworkStatus from "../components/status/NetworkStatus";
import InternetStatus from "../components/status/InternetStatus";
import PerformanceStatus from "../components/status/PerformanceStatus";
import SettingsPanel from "../components/settings/SettingsPanel";
import SuggestionsList from "../components/suggestions/SuggestionsList";
import logo from "../assets/logo.png";

export default function Dashboard() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [settings, setSettings] = useState({
    api_url: "http://localhost:8088",
    voice_mode_enabled: false
  });
  const [networkData, setNetworkData] = useState(null);
  const [aiData, setAiData] = useState(null);
  const [user, setUser] = useState(null);

  const queryClient = useQueryClient();

  // Get current user
  useEffect(() => {
    const loadUser = async () => {
      try {
        const currentUser = await base44.auth.me();
        setUser(currentUser);
        
        // Load user settings
        const userSettings = await base44.entities.AppSettings.filter({
          user_email: currentUser.email
        });
        
        if (userSettings.length > 0) {
          setSettings(userSettings[0]);
        } else {
          // Create default settings
          const newSettings = await base44.entities.AppSettings.create({
            user_email: currentUser.email,
            api_url: "http://localhost:8088",
            voice_mode_enabled: false
          });
          setSettings(newSettings);
        }
      } catch (err) {
        console.error("Error loading user:", err);
      }
    };
    loadUser();
  }, []);

  // Load chat messages
  const { data: messages = [], isLoading: messagesLoading } = useQuery({
    queryKey: ['chatMessages', user?.email],
    queryFn: () => base44.entities.ChatMessage.filter({ created_by: user.email }, '-created_date'),
    enabled: !!user,
    initialData: [],
  });

  // Create message mutation
  const createMessageMutation = useMutation({
    mutationFn: (messageData) => base44.entities.ChatMessage.create(messageData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chatMessages'] });
    },
  });

  // Update settings mutation
  const updateSettingsMutation = useMutation({
    mutationFn: (settingsData) => base44.entities.AppSettings.update(settings.id, settingsData),
    onSuccess: (data) => {
      setSettings(data);
    },
  });

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
    if (!user) return;
    
    setIsProcessing(true);
    setError(null);

    try {
      // Add user message
      await createMessageMutation.mutateAsync({
        role: "user",
        content: content
      });

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
        
        // Clean up response - remove asterisks and extra formatting
        let cleanedResponse = (data.response || "Sorry, I could not process your request.")
          .replace(/\*\*/g, '')  // Remove bold markdown
          .replace(/\*/g, '')    // Remove asterisks
          .trim();
        
        // Add AI response
        await createMessageMutation.mutateAsync({
          role: "assistant",
          content: cleanedResponse,
          audio_url: data.audio_url ? `${settings.api_url}${data.audio_url}` : undefined,
          ai_model_used: data.ai_model_used || false,
          rag_enabled: data.rag_enabled || false
        });
      } else {
        throw new Error("Failed to get AI response");
      }
    } catch (err) {
      console.error("Error:", err);
      setError("Failed to communicate with AI brain. Please check if the API server is running.");
      
      // Add error message
      await createMessageMutation.mutateAsync({
        role: "assistant",
        content: "Sorry, I'm having trouble connecting right now. Please try again later."
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleVoiceInput = async (audioBlob) => {
    setIsProcessing(true);
    setError(null);

    try {
      // Create FormData and append the audio file
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');

      // Send audio to backend for transcription (relative URL since it's on the same server)
      const response = await fetch(`/api/voice`, {
        method: "POST",
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        
        if (data.success && data.transcription) {
          // Send transcription as regular message
          await handleSendMessage(data.transcription);
        } else {
          throw new Error("Failed to transcribe audio");
        }
      } else {
        throw new Error("Failed to process voice input");
      }
    } catch (err) {
      console.error("Voice input error:", err);
      setError("Failed to process voice input. Please try again.");
      
      // Still show an error message
      await createMessageMutation.mutateAsync({
        role: "assistant",
        content: "Sorry, I couldn't process your voice input. Please try typing instead or check if the microphone is working."
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleUpdateSettings = async (newSettings) => {
    if (settings.id) {
      await updateSettingsMutation.mutateAsync(newSettings);
    } else {
      setSettings(newSettings);
    }
  };

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="backdrop-blur-xl bg-white/10 border border-white/20 rounded-2xl p-8">
          <Loader2 className="w-8 h-8 text-white animate-spin mx-auto" />
          <p className="text-white mt-4">Loading...</p>
        </div>
      </div>
    );
  }

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
            >
              {messagesLoading ? (
                <div className="flex items-center justify-center h-full">
                  <Loader2 className="w-8 h-8 text-white animate-spin" />
                </div>
              ) : messages.length === 0 ? (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <div className="w-32 h-32 mx-auto mb-4 flex items-center justify-center">
                      <img src={logo} alt="IT-Mobile Logo" className="w-full h-full object-contain" />
                    </div>
                    <h3 className="text-xl font-semibold text-white mb-2">
                      Welcome to IT-Mobile
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
                  <div className="flex-shrink-0 w-10 h-10 flex items-center justify-center">
                    <img src={logo} alt="IT-Mobile" className="w-10 h-10 object-contain" />
                  </div>
                  <div className="backdrop-blur-xl bg-white/10 border border-white/20 rounded-2xl px-4 py-3">
                    <div className="flex items-center gap-2">
                      <Loader2 className="w-4 h-4 text-white animate-spin" />
                      <span className="text-white text-sm">IT-Mobile is analyzing...</span>
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


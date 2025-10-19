import React, { useState } from "react";
import { Send, Mic, MicOff, Loader2 } from "lucide-react";
import { Button } from "../ui/Button";
import { Textarea } from "../ui/Textarea";
import { motion } from "framer-motion";

export default function ChatInput({ onSendMessage, onVoiceInput, isProcessing }) {
  const [message, setMessage] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [currentTranscript, setCurrentTranscript] = useState("");

  const handleSend = () => {
    if (message.trim() && !isProcessing) {
      onSendMessage(message);
      setMessage("");
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks = [];

      recorder.ondataavailable = (e) => chunks.push(e.data);
      recorder.onstop = () => {
        const blob = new Blob(chunks, { type: "audio/webm" });
        // Pass both the audio blob and the recognition object with transcript
        onVoiceInput(blob, recorder.recognitionData);
        stream.getTracks().forEach(track => track.stop());
      };

      recorder.start();
      setMediaRecorder(recorder);
      setIsRecording(true);
      setCurrentTranscript("");
      
      // Start speech recognition simultaneously
      if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';
        
        recognition.onresult = (event) => {
          let transcript = '';
          for (let i = 0; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
          }
          setCurrentTranscript(transcript);
          // Store transcript in recorder
          recorder.recognitionData = { transcript };
        };
        
        recognition.onerror = (event) => {
          console.error('Speech recognition error:', event.error);
        };
        
        recognition.start();
        
        // Store recognition in recorder for later access
        recorder.recognition = recognition;
      }
    } catch (error) {
      console.error("Error accessing microphone:", error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && isRecording) {
      // Stop speech recognition if it exists
      if (mediaRecorder.recognition) {
        mediaRecorder.recognition.stop();
      }
      
      mediaRecorder.stop();
      setIsRecording(false);
      setMediaRecorder(null);
    }
  };

  return (
    <div className="backdrop-blur-xl bg-white/10 border border-white/20 rounded-2xl p-4"
      style={{
        boxShadow: "0 8px 32px 0 rgba(31, 38, 135, 0.37)",
      }}
    >
      <div className="flex gap-3">
        <div className="flex-1 relative">
          <Textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask the AI brain about your network..."
            disabled={isProcessing}
            className="min-h-[60px] bg-white/5 border-white/20 text-white placeholder:text-purple-200/50 resize-none backdrop-blur-sm"
            style={{
              boxShadow: "inset 0 2px 10px rgba(0, 0, 0, 0.1)",
            }}
          />
        </div>
        
        <div className="flex flex-col gap-2">
          <Button
            onClick={isRecording ? stopRecording : startRecording}
            disabled={isProcessing}
            className={`backdrop-blur-xl border border-white/20 ${
              isRecording 
                ? "bg-red-500/30 hover:bg-red-500/40 text-white" 
                : "bg-purple-500/30 hover:bg-purple-500/40 text-white"
            }`}
            size="icon"
          >
            {isRecording ? (
              <motion.div
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ repeat: Infinity, duration: 1 }}
              >
                <MicOff className="w-5 h-5" />
              </motion.div>
            ) : (
              <Mic className="w-5 h-5" />
            )}
          </Button>
          
          <Button
            onClick={handleSend}
            disabled={!message.trim() || isProcessing}
            className="bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white border border-white/20 backdrop-blur-xl"
            size="icon"
          >
            {isProcessing ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </Button>
        </div>
      </div>
      
      <div className="mt-2 text-xs text-purple-200/70">
        {isRecording && currentTranscript ? (
          <div className="flex items-center gap-2">
            <motion.div
              animate={{ opacity: [1, 0.5, 1] }}
              transition={{ repeat: Infinity, duration: 1.5 }}
              className="w-2 h-2 bg-red-500 rounded-full"
            />
            <span className="text-white">Listening: "{currentTranscript}"</span>
          </div>
        ) : isRecording ? (
          <div className="flex items-center gap-2">
            <motion.div
              animate={{ opacity: [1, 0.5, 1] }}
              transition={{ repeat: Infinity, duration: 1.5 }}
              className="w-2 h-2 bg-red-500 rounded-full"
            />
            <span>Listening... Speak now</span>
          </div>
        ) : (
          "Press Enter to send • Shift+Enter for new line • Click mic to record"
        )}
      </div>
    </div>
  );
}


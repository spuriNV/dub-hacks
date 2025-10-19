import React, { useState } from "react";
import { Send, Mic, MicOff, Loader2 } from "lucide-react";
import { Button } from "../ui/button";
import { Textarea } from "../ui/textarea";
import { motion } from "framer-motion";

export default function ChatInput({ onSendMessage, onVoiceInput, isProcessing }) {
  const [message, setMessage] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [recognition, setRecognition] = useState(null);
  const [transcript, setTranscript] = useState("");
  const [isTranscribing, setIsTranscribing] = useState(false);

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
      // Reset transcript
      setTranscript("");
      setIsTranscribing(true);
      
      // Start audio recording to save to server
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks = [];

      recorder.ondataavailable = (e) => chunks.push(e.data);
      
      // Check if browser supports Web Speech API
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      
      if (SpeechRecognition) {
        // Use Web Speech API for real-time transcription
        const recognitionInstance = new SpeechRecognition();
        recognitionInstance.continuous = true;  // Keep listening
        recognitionInstance.interimResults = true;  // Show interim results
        recognitionInstance.lang = 'en-US';
        
        let finalText = '';

        recognitionInstance.onresult = async (event) => {
          let interimTranscript = '';
          let currentFinalTranscript = '';
          
          // Combine all results
          for (let i = 0; i < event.results.length; i++) {
            const transcriptPiece = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              currentFinalTranscript += transcriptPiece + ' ';
            } else {
              interimTranscript += transcriptPiece;
            }
          }
          
          // Store the final transcript
          if (currentFinalTranscript) {
            finalText = currentFinalTranscript.trim();
            setTranscript(finalText);
          } else if (interimTranscript) {
            setTranscript(finalText + ' ' + interimTranscript);
          }
        };

        recognitionInstance.onerror = (event) => {
          console.error("Speech recognition error:", event.error);
          setIsTranscribing(false);
          if (event.error === 'not-allowed') {
            alert('Microphone access denied. Please allow microphone access and try again.');
          }
        };
        
        recognitionInstance.onend = async () => {
          console.log("Recognition ended, final text:", finalText);
          setIsTranscribing(false);
          setIsRecording(false);
          
          // Stop audio recording
          if (recorder.state !== 'inactive') {
            recorder.stop();
          }
          stream.getTracks().forEach(track => track.stop());
          
          // Send the final transcript
          if (finalText.trim()) {
            // Save the audio file to server in background
            const audioBlob = new Blob(chunks, { type: "audio/webm" });
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');
            
            // Send to server to save (don't wait for response)
            fetch('/api/voice', {
              method: 'POST',
              body: formData
            }).catch(err => console.error("Failed to save recording:", err));
            
            // Send transcription as a message
            onSendMessage(finalText.trim());
            setTranscript("");
          }
        };

        recognitionInstance.start();
        setRecognition(recognitionInstance);
      } else {
        // Fallback: recording only, send to server for transcription
        setTranscript("Speech recognition not supported. Recording audio...");
        recorder.onstop = () => {
          const blob = new Blob(chunks, { type: "audio/webm" });
          onVoiceInput(blob);
          stream.getTracks().forEach(track => track.stop());
          setTranscript("");
          setIsTranscribing(false);
        };
      }

      recorder.start();
      setMediaRecorder(recorder);
      setIsRecording(true);
    } catch (error) {
      console.error("Error accessing microphone:", error);
      setIsTranscribing(false);
      alert(`Microphone error: ${error.message}. Please check your microphone permissions.`);
    }
  };

  const stopRecording = () => {
    if (recognition && isRecording) {
      recognition.stop();
      setRecognition(null);
      setIsRecording(false);
    } else if (mediaRecorder && isRecording) {
      mediaRecorder.stop();
      setIsRecording(false);
      setMediaRecorder(null);
    }
    setIsTranscribing(false);
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
      
      {/* Real-time transcription display */}
      {(isTranscribing || transcript) && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-3 backdrop-blur-xl bg-blue-500/20 border border-blue-400/30 rounded-xl p-3"
        >
          <div className="flex items-center gap-2 mb-2">
            <motion.div
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ repeat: Infinity, duration: 1.5 }}
              className="w-2 h-2 rounded-full bg-red-400"
            />
            <span className="text-xs text-blue-200 font-medium">
              {isTranscribing ? "Listening..." : "Transcription complete"}
            </span>
          </div>
          <p className="text-sm text-white leading-relaxed">
            {transcript || "Start speaking..."}
          </p>
        </motion.div>
      )}
      
      <div className="mt-2 text-xs text-purple-200/70">
        Press Enter to send • Shift+Enter for new line • Click mic to record voice
      </div>
    </div>
  );
}


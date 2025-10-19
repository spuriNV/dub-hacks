import React from "react";
import { User, Bot, Volume2 } from "lucide-react";
import { motion } from "framer-motion";
import { Button } from "../ui/button";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "../ui/collapsible";
import { ChevronDown } from "lucide-react";

export default function MessageBubble({ message, index }) {
  const isUser = message.role === "user";
  const [isOpen, setIsOpen] = React.useState(false);
  const [isPlaying, setIsPlaying] = React.useState(false);
  const audioRef = React.useRef(null);

  // Auto-play audio when message with audio arrives
  React.useEffect(() => {
    if (message.audio_url && audioRef.current && !isUser) {
      audioRef.current.play().catch(err => {
        console.log("Auto-play prevented:", err);
      });
    }
  }, [message.audio_url, isUser]);

  const toggleAudio = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className={`flex gap-3 mb-4 ${isUser ? "justify-end" : "justify-start"}`}
    >
      {!isUser && (
        <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center backdrop-blur-xl border border-white/20">
          <Bot className="w-5 h-5 text-white" />
        </div>
      )}
      
      <div className={`flex flex-col gap-2 max-w-[70%] ${isUser ? "items-end" : "items-start"}`}>
        <div
          className={`px-4 py-3 rounded-2xl backdrop-blur-xl border border-white/20 ${
            isUser
              ? "bg-gradient-to-br from-blue-500/20 to-purple-500/20 text-white"
              : "bg-white/10 text-white"
          }`}
          style={{
            boxShadow: "0 8px 32px 0 rgba(31, 38, 135, 0.37)",
          }}
        >
          <p className="text-sm leading-relaxed">{message.content}</p>
        </div>

        {!isUser && (
          <div className="flex flex-col gap-2 w-full">
            {message.audio_url && (
              <div className="backdrop-blur-xl bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-400/30 rounded-xl p-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <motion.div
                      animate={isPlaying ? { scale: [1, 1.2, 1] } : {}}
                      transition={{ repeat: isPlaying ? Infinity : 0, duration: 0.8 }}
                    >
                      <Volume2 className="w-4 h-4 text-purple-300" />
                    </motion.div>
                    <span className="text-xs text-purple-200 font-medium">
                      {isPlaying ? "🔊 Playing..." : "🎵 Voice Response"}
                    </span>
                  </div>
                  <button
                    onClick={toggleAudio}
                    className="text-xs text-purple-300 hover:text-purple-100 transition-colors"
                  >
                    {isPlaying ? "⏸ Pause" : "▶ Play"}
                  </button>
                </div>
                <audio 
                  ref={audioRef}
                  controls 
                  className="w-full h-8"
                  onPlay={() => setIsPlaying(true)}
                  onPause={() => setIsPlaying(false)}
                  onEnded={() => setIsPlaying(false)}
                  style={{
                    filter: "drop-shadow(0 0 10px rgba(168, 85, 247, 0.4))"
                  }}
                >
                  <source src={message.audio_url} type="audio/wav" />
                </audio>
              </div>
            )}

            {(message.ai_model_used !== undefined || message.rag_enabled !== undefined) && (
              <Collapsible open={isOpen} onOpenChange={setIsOpen}>
                <CollapsibleTrigger asChild>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="backdrop-blur-xl bg-white/5 border border-white/20 text-white hover:bg-white/10 text-xs h-7"
                  >
                    AI Analysis Details
                    <ChevronDown className={`w-3 h-3 ml-1 transition-transform ${isOpen ? "rotate-180" : ""}`} />
                  </Button>
                </CollapsibleTrigger>
                <CollapsibleContent>
                  <div className="mt-2 backdrop-blur-xl bg-white/10 border border-white/20 rounded-xl p-3 text-xs space-y-1">
                    <div className="flex justify-between">
                      <span className="text-purple-200">AI Model:</span>
                      <span className="text-white font-medium">
                        {message.ai_model_used ? "Qwen/Qwen2-0.5B" : "Rule-based"}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-purple-200">RAG Knowledge:</span>
                      <span className="text-white font-medium">
                        {message.rag_enabled ? "Enabled" : "Disabled"}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-purple-200">Voice Response:</span>
                      <span className="text-white font-medium">
                        {message.audio_url ? "Yes" : "No"}
                      </span>
                    </div>
                  </div>
                </CollapsibleContent>
              </Collapsible>
            )}
          </div>
        )}
      </div>

      {isUser && (
        <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center backdrop-blur-xl border border-white/20">
          <User className="w-5 h-5 text-white" />
        </div>
      )}
    </motion.div>
  );
}


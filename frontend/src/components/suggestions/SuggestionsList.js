import React from "react";
import { Lightbulb, Sparkles } from "lucide-react";
import { motion } from "framer-motion";

const suggestions = [
  "What's wrong with my WiFi?",
  "My internet is slow, help me",
  "How can I improve my signal?",
  "Check my network security",
  "Why is my connection dropping?"
];

export default function SuggestionsList({ onSelectSuggestion }) {
  return (
    <div className="backdrop-blur-xl bg-gradient-to-br from-amber-500/20 to-yellow-500/20 border border-white/20 rounded-2xl p-4 mb-4"
      style={{
        boxShadow: "0 8px 32px 0 rgba(31, 38, 135, 0.37)",
      }}
    >
      <div className="flex items-center gap-2 mb-3">
        <Lightbulb className="w-4 h-4 text-yellow-300" />
        <h3 className="text-white font-semibold text-sm">Ask the AI Brain</h3>
      </div>
      <div className="space-y-2">
        {suggestions.map((suggestion, index) => (
          <motion.button
            key={index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            onClick={() => onSelectSuggestion(suggestion)}
            className="w-full text-left px-3 py-2 rounded-lg bg-white/10 hover:bg-white/20 border border-white/20 text-white text-xs transition-all backdrop-blur-sm flex items-center gap-2 group"
          >
            <Sparkles className="w-3 h-3 text-yellow-300 group-hover:scale-110 transition-transform" />
            {suggestion}
          </motion.button>
        ))}
      </div>
    </div>
  );
}


import React from "react";
import { Lightbulb } from "lucide-react";
import StatusCard from "../status/StatusCard";
import { Button } from "../ui/button";

export default function SuggestionsList({ onSelectSuggestion }) {
  const suggestions = [
    "What is my current network status?",
    "Check WiFi signal strength",
    "Is my internet connection stable?",
    "Show network performance metrics",
    "Diagnose network issues"
  ];

  return (
    <StatusCard
      title="Quick Questions"
      icon={Lightbulb}
      gradient="from-amber-500/20 to-yellow-500/20"
    >
      <div className="space-y-2">
        {suggestions.map((suggestion, index) => (
          <Button
            key={index}
            onClick={() => onSelectSuggestion(suggestion)}
            variant="ghost"
            className="w-full text-left text-xs backdrop-blur-xl bg-white/5 border border-white/20 text-white hover:bg-white/10 justify-start h-auto py-2 px-3"
          >
            {suggestion}
          </Button>
        ))}
      </div>
    </StatusCard>
  );
}


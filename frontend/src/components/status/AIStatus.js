import React from "react";
import { Brain, Database, Volume2 } from "lucide-react";
import StatusCard from "./StatusCard";

export default function AIStatus({ aiData }) {
  if (!aiData) {
    return (
      <StatusCard
        title="AI Brain Status"
        icon={Brain}
        status="error"
        statusColor="error"
        gradient="from-red-500/20 to-pink-500/20"
      >
        <p className="text-red-200 text-xs">Unable to get AI status</p>
      </StatusCard>
    );
  }

  return (
    <div className="space-y-4">
      <StatusCard
        title="AI Model"
        icon={Brain}
        status={aiData.ai_model_loaded}
        statusColor={aiData.ai_model_loaded ? "good" : "warning"}
        gradient="from-pink-500/20 to-rose-500/20"
      >
        <div className="flex justify-between">
          <span className="text-pink-200">Status:</span>
          <span className="text-white font-medium">
            {aiData.ai_model_loaded ? "distilgpt2 Loaded" : "Rule-based Mode"}
          </span>
        </div>
      </StatusCard>

      <StatusCard
        title="RAG Knowledge"
        icon={Database}
        status={aiData.rag_enabled}
        statusColor={aiData.rag_enabled ? "good" : "error"}
        gradient="from-indigo-500/20 to-purple-500/20"
      >
        {aiData.rag_enabled ? (
          <div className="flex justify-between">
            <span className="text-indigo-200">Items Loaded:</span>
            <span className="text-white font-medium">{aiData.knowledge_base_size || 0}</span>
          </div>
        ) : (
          <p className="text-red-200">Not Available</p>
        )}
      </StatusCard>

      <StatusCard
        title="Voice (TTS)"
        icon={Volume2}
        status={aiData.tts_available}
        statusColor={aiData.tts_available ? "good" : "error"}
        gradient="from-cyan-500/20 to-blue-500/20"
      >
        <div className="flex justify-between">
          <span className="text-cyan-200">Status:</span>
          <span className="text-white font-medium">
            {aiData.tts_available ? "Piper Available" : "Not Available"}
          </span>
        </div>
      </StatusCard>
    </div>
  );
}


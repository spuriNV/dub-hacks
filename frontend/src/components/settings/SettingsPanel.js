import React from "react";
import { Settings, Volume2, Server } from "lucide-react";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Switch } from "../ui/switch";
import StatusCard from "../status/StatusCard";

export default function SettingsPanel({ settings, onUpdateSettings }) {
  return (
    <div className="space-y-4">
      <StatusCard
        title="Settings"
        icon={Settings}
        gradient="from-slate-500/20 to-gray-500/20"
      >
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="api-url" className="text-white text-xs flex items-center gap-2">
              <Server className="w-3 h-3" />
              API URL
            </Label>
            <Input
              id="api-url"
              value={settings.api_url}
              onChange={(e) => onUpdateSettings({ ...settings, api_url: e.target.value })}
              className="bg-white/5 border-white/20 text-white text-xs h-8"
              placeholder="http://localhost:8088"
            />
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="voice-mode" className="text-white text-xs flex items-center gap-2">
                <Volume2 className="w-3 h-3" />
                Text-to-Speech (TTS)
              </Label>
              <Switch
                id="voice-mode"
                checked={settings.voice_mode_enabled}
                onCheckedChange={(checked) => 
                  onUpdateSettings({ ...settings, voice_mode_enabled: checked })
                }
              />
            </div>
            <p className="text-xs text-purple-200/70 ml-5">
              {settings.voice_mode_enabled 
                ? "✅ AI will narrate responses using Piper TTS" 
                : "🔇 Voice responses disabled"}
            </p>
          </div>
        </div>
      </StatusCard>
    </div>
  );
}


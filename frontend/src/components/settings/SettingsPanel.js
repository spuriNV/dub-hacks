import React from "react";
import { Settings, Volume2, Server } from "lucide-react";
import { Input } from "../ui/Input";
import { Label } from "../ui/Label";
import { Switch } from "../ui/Switch";
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

          <div className="flex items-center justify-between">
            <Label htmlFor="voice-mode" className="text-white text-xs flex items-center gap-2">
              <Volume2 className="w-3 h-3" />
              Voice Responses
            </Label>
            <Switch
              id="voice-mode"
              checked={settings.voice_mode_enabled}
              onCheckedChange={(checked) => 
                onUpdateSettings({ ...settings, voice_mode_enabled: checked })
              }
            />
          </div>
        </div>
      </StatusCard>
    </div>
  );
}


import React from "react";
import { Wifi } from "lucide-react";
import StatusCard from "./StatusCard";

export default function NetworkStatus({ networkData }) {
  if (!networkData) {
    return (
      <StatusCard
        title="Network Status"
        icon={Wifi}
        status="error"
        statusColor="error"
        gradient="from-red-500/20 to-orange-500/20"
      >
        <p className="text-red-200 text-xs">Unable to connect to AI brain</p>
      </StatusCard>
    );
  }

  const wifi = networkData.wifi || {};

  return (
    <StatusCard
      title="Network Status"
      icon={Wifi}
      status={wifi.status === "connected"}
      statusColor={wifi.status === "connected" ? "good" : "error"}
      gradient="from-blue-500/20 to-cyan-500/20"
    >
      {wifi.status === "connected" ? (
        <>
          <div className="flex justify-between">
            <span className="text-cyan-200">Connected to:</span>
            <span className="text-white font-medium">{wifi.ssid || "Unknown"}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-cyan-200">Signal:</span>
            <span className="text-white font-medium">{wifi.signal_strength || "N/A"} dBm</span>
          </div>
        </>
      ) : (
        <p className="text-red-200">Not Connected</p>
      )}
    </StatusCard>
  );
}


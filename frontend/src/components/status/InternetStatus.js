import React from "react";
import { Globe } from "lucide-react";
import StatusCard from "./StatusCard";

export default function InternetStatus({ networkData }) {
  if (!networkData) {
    return (
      <StatusCard
        title="Internet Status"
        icon={Globe}
        status="error"
        statusColor="error"
        gradient="from-red-500/20 to-orange-500/20"
      >
        <p className="text-red-200 text-xs">Unable to connect to AI brain</p>
      </StatusCard>
    );
  }

  const connectivity = networkData.connectivity || {};

  return (
    <StatusCard
      title="Internet Status"
      icon={Globe}
      status={connectivity.internet_connected}
      statusColor={connectivity.internet_connected ? "good" : "error"}
      gradient="from-purple-500/20 to-indigo-500/20"
    >
      {connectivity.internet_connected ? (
        <>
          <div className="flex justify-between">
            <span className="text-purple-200">Status:</span>
            <span className="text-white font-medium">Connected</span>
          </div>
          <div className="flex justify-between">
            <span className="text-purple-200">Latency:</span>
            <span className="text-white font-medium">{connectivity.latency || "N/A"}</span>
          </div>
        </>
      ) : (
        <p className="text-red-200">Not Connected</p>
      )}
    </StatusCard>
  );
}


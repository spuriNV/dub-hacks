import React from "react";
import { Zap } from "lucide-react";
import StatusCard from "./StatusCard";

export default function PerformanceStatus({ networkData }) {
  if (!networkData) {
    return (
      <StatusCard
        title="Performance"
        icon={Zap}
        status="error"
        statusColor="error"
        gradient="from-red-500/20 to-orange-500/20"
      >
        <p className="text-red-200 text-xs">Unable to connect to AI brain</p>
      </StatusCard>
    );
  }

  const performance = networkData.performance || {};
  
  const getStatusColor = () => {
    const quality = performance.network_quality;
    if (quality === "excellent" || quality === "good") return "good";
    if (quality === "fair") return "warning";
    return "error";
  };

  return (
    <StatusCard
      title="Performance"
      icon={Zap}
      status={true}
      statusColor={getStatusColor()}
      gradient="from-yellow-500/20 to-orange-500/20"
    >
      <div className="flex justify-between">
        <span className="text-yellow-200">Quality:</span>
        <span className="text-white font-medium capitalize">
          {performance.network_quality || "Unknown"}
        </span>
      </div>
      <div className="flex justify-between">
        <span className="text-yellow-200">Active Connections:</span>
        <span className="text-white font-medium">{performance.active_connections || 0}</span>
      </div>
    </StatusCard>
  );
}


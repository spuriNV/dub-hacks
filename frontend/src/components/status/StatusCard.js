import React from "react";
import { motion } from "framer-motion";

export default function StatusCard({ 
  title, 
  icon: Icon, 
  status, 
  statusColor, 
  children,
  gradient = "from-purple-500/20 to-pink-500/20"
}) {
  const statusColors = {
    good: "bg-green-400",
    warning: "bg-yellow-400",
    error: "bg-red-400"
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`backdrop-blur-xl bg-gradient-to-br ${gradient} border border-white/20 rounded-2xl p-4 mb-4`}
      style={{
        boxShadow: "0 8px 32px 0 rgba(31, 38, 135, 0.37)",
      }}
    >
      <div className="flex items-center gap-3 mb-3">
        <div className="w-10 h-10 rounded-xl bg-white/10 backdrop-blur-sm flex items-center justify-center border border-white/20">
          <Icon className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1">
          <h3 className="text-white font-semibold text-sm">{title}</h3>
        </div>
        {status && (
          <div className={`w-3 h-3 rounded-full ${statusColors[statusColor]} shadow-lg`}
            style={{
              boxShadow: `0 0 10px ${statusColor === 'good' ? '#4ade80' : statusColor === 'warning' ? '#fbbf24' : '#f87171'}`
            }}
          />
        )}
      </div>
      <div className="space-y-2 text-sm">
        {children}
      </div>
    </motion.div>
  );
}


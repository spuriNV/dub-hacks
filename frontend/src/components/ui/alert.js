import React from "react";

export function Alert({ children, variant = "default", className = "" }) {
  const variants = {
    default: "bg-white border-gray-200",
    destructive: "border-red-500/50 text-red-600"
  };

  return (
    <div
      className={`relative w-full rounded-lg border p-4 ${variants[variant]} ${className}`}
      role="alert"
    >
      {children}
    </div>
  );
}

export function AlertDescription({ children, className = "" }) {
  return (
    <div className={`text-sm ${className}`}>
      {children}
    </div>
  );
}


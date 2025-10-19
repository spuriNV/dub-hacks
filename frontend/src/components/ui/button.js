import React from "react";

export function Button({ 
  children, 
  onClick, 
  disabled, 
  className = "", 
  variant = "default", 
  size = "default",
  ...props 
}) {
  const baseStyles = "inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none";
  
  const variants = {
    default: "bg-blue-600 text-white hover:bg-blue-700",
    ghost: "hover:bg-white/10 text-white",
    destructive: "bg-red-600 text-white hover:bg-red-700"
  };
  
  const sizes = {
    default: "h-10 py-2 px-4",
    sm: "h-8 px-3 text-xs",
    lg: "h-12 px-8",
    icon: "h-10 w-10"
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}


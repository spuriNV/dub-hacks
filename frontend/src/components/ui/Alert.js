import React from "react";
import { AlertCircle, CheckCircle, Info, AlertTriangle } from "lucide-react";

const Alert = React.forwardRef(({ className = "", variant = "default", children, ...props }, ref) => {
  const variants = {
    default: "bg-background text-foreground",
    destructive: "border-destructive/50 text-destructive dark:border-destructive [&>svg]:text-destructive"
  };
  
  return (
    <div
      ref={ref}
      role="alert"
      className={`relative w-full rounded-lg border p-4 [&>svg~*]:pl-7 [&>svg+div]:translate-y-[-3px] [&>svg]:absolute [&>svg]:left-4 [&>svg]:top-4 [&>svg]:text-foreground ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
});

const AlertDescription = React.forwardRef(({ className = "", ...props }, ref) => {
  return (
    <div
      ref={ref}
      className={`text-sm [&_p]:leading-relaxed ${className}`}
      {...props}
    />
  );
});

Alert.displayName = "Alert";
AlertDescription.displayName = "AlertDescription";

export { Alert, AlertDescription };


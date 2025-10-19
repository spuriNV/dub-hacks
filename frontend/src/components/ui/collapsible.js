import React from "react";

export function Collapsible({ open, onOpenChange, children }) {
  return (
    <div>
      {React.Children.map(children, child =>
        React.cloneElement(child, { open, onOpenChange })
      )}
    </div>
  );
}

export function CollapsibleTrigger({ children, asChild, open, onOpenChange }) {
  if (asChild) {
    return React.cloneElement(children, {
      onClick: () => onOpenChange(!open)
    });
  }
  return <div onClick={() => onOpenChange(!open)}>{children}</div>;
}

export function CollapsibleContent({ children, open }) {
  if (!open) return null;
  return <div>{children}</div>;
}


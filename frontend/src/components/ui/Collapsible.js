import React from "react";

const CollapsibleContext = React.createContext();

const Collapsible = ({ open, onOpenChange, children, ...props }) => {
  return (
    <CollapsibleContext.Provider value={{ open, onOpenChange }}>
      <div {...props}>
        {children}
      </div>
    </CollapsibleContext.Provider>
  );
};

const CollapsibleTrigger = React.forwardRef(({ asChild, children, ...props }, ref) => {
  const { open, onOpenChange } = React.useContext(CollapsibleContext);
  
  if (asChild) {
    return React.cloneElement(children, {
      onClick: () => onOpenChange(!open),
      ref,
      ...props
    });
  }
  
  return (
    <button
      ref={ref}
      onClick={() => onOpenChange(!open)}
      {...props}
    >
      {children}
    </button>
  );
});

const CollapsibleContent = React.forwardRef(({ children, className = "", ...props }, ref) => {
  const { open } = React.useContext(CollapsibleContext);
  
  if (!open) return null;
  
  return (
    <div
      ref={ref}
      className={className}
      {...props}
    >
      {children}
    </div>
  );
});

CollapsibleTrigger.displayName = "CollapsibleTrigger";
CollapsibleContent.displayName = "CollapsibleContent";

export { Collapsible, CollapsibleTrigger, CollapsibleContent };


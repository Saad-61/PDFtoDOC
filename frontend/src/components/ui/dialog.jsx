import React, { useEffect } from "react";
import { cn } from "../../utils/cn";
import { X } from "lucide-react";

export function Dialog({ open, onClose, children, className }) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape" && open) {
        onClose?.();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-carbon-950/80 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Modal Dialog Card */}
      <div
        className={cn(
          "relative z-10 w-full max-w-lg bg-carbon-800 border border-slate-border rounded-md shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200",
          className
        )}
      >
        {children}
      </div>
    </div>
  );
}

export function DialogHeader({ className, children }) {
  return (
    <div className={cn("p-6 pb-3 border-b border-slate-border/50", className)}>
      {children}
    </div>
  );
}

export function DialogTitle({ className, children }) {
  return (
    <h3
      className={cn(
        "font-display text-2xl font-semibold text-ivory tracking-tight",
        className
      )}
    >
      {children}
    </h3>
  );
}

export function DialogDescription({ className, children }) {
  return (
    <p className={cn("text-xs text-taupe mt-1 leading-relaxed", className)}>
      {children}
    </p>
  );
}

export function DialogContent({ className, children }) {
  return <div className={cn("p-6", className)}>{children}</div>;
}

export function DialogFooter({ className, children }) {
  return (
    <div
      className={cn(
        "p-6 pt-4 border-t border-slate-border/50 flex items-center justify-end gap-3",
        className
      )}
    >
      {children}
    </div>
  );
}

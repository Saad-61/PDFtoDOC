import React from "react";
import { cn } from "../../utils/cn";

export function Badge({
  className,
  variant = "default",
  children,
  ...props
}) {
  const variants = {
    default: "bg-carbon-700 text-taupe border-slate-border",
    gold: "bg-gold-500/10 text-gold-400 border-gold-500/30",
    forest: "bg-forest-surface text-forest-light border-forest/40",
    oxblood: "bg-oxblood-surface text-oxblood-light border-oxblood/40",
    brass: "bg-brass-surface text-brass border-brass/40",
    outline: "bg-transparent text-ivory border-slate-border",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-mono font-medium border",
        variants[variant],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}

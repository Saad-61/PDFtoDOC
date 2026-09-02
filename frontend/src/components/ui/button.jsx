import React from "react";
import { cn } from "../../utils/cn";

export const Button = React.forwardRef(
  (
    {
      className,
      variant = "default",
      size = "default",
      disabled = false,
      children,
      ...props
    },
    ref
  ) => {
    const baseStyles =
      "inline-flex items-center justify-center font-medium transition-all duration-150 rounded-sm focus:outline-none focus:ring-1 focus:ring-gold-500/50 disabled:opacity-40 disabled:cursor-not-allowed disabled:pointer-events-none btn-tactile select-none";

    const variants = {
      default:
        "bg-gold-500 text-carbon-950 hover:bg-gold-400 active:bg-gold-600 shadow-md font-semibold tracking-wide",
      secondary:
        "bg-carbon-800 text-ivory border border-slate-border hover:border-slate-border-light hover:bg-carbon-700",
      outline:
        "border border-gold-500/70 text-gold-400 hover:bg-gold-500/10 hover:text-gold-300 hover:border-gold-400",
      ghost:
        "text-taupe hover:text-ivory hover:bg-carbon-800/80",
      danger:
        "bg-oxblood text-ivory hover:bg-oxblood-light border border-oxblood-light/40",
      forest:
        "bg-forest text-ivory hover:bg-forest-light border border-forest-light/40",
    };

    const sizes = {
      sm: "text-xs px-3 py-1.5 h-8 gap-1.5",
      default: "text-sm px-4 py-2 h-10 gap-2",
      lg: "text-base px-6 py-3 h-12 gap-2.5 font-medium",
      icon: "h-9 w-9 p-0",
    };

    return (
      <button
        ref={ref}
        disabled={disabled}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";

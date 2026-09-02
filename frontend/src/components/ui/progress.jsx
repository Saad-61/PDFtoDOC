import React from "react";
import { cn } from "../../utils/cn";

export function Progress({ value = 0, max = 100, className, showShimmer = true }) {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));

  return (
    <div
      className={cn(
        "w-full bg-carbon-950 border border-slate-border h-2.5 rounded-full overflow-hidden relative",
        className
      )}
    >
      <div
        className={cn(
          "h-full bg-gradient-to-r from-gold-600 via-gold-500 to-gold-400 transition-all duration-300 ease-out rounded-full relative",
          showShimmer && percentage < 100 && "shimmer-liquid"
        )}
        style={{ width: `${percentage}%` }}
      />
    </div>
  );
}

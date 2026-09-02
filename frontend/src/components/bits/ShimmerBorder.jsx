import React from "react";
import { cn } from "../../utils/cn";

export function ShimmerBorder({
  children,
  className,
  active = false,
  borderRadius = "rounded-md",
}) {
  return (
    <div className={cn("relative p-[1px] group", borderRadius, className)}>
      {active && (
        <div
          className={cn(
            "absolute inset-0 bg-gradient-to-r from-gold-500/20 via-gold-400 to-gold-500/20 animate-pulse-slow opacity-80",
            borderRadius
          )}
        />
      )}
      <div className={cn("relative h-full w-full bg-carbon-800", borderRadius)}>
        {children}
      </div>
    </div>
  );
}

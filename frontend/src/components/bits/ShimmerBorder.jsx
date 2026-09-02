import React from "react";
import { cn } from "../../utils/cn";

export function ShimmerBorder({
  children,
  className,
  active = false,
  borderRadius = "rounded-md",
}) {
  return (
    <div
      className={cn(
        "relative rounded-md transition-all duration-150",
        active ? "border-gold-500" : "border-transparent",
        borderRadius,
        className
      )}
    >
      <div className={cn("relative h-full w-full bg-carbon-800", borderRadius)}>
        {children}
      </div>
    </div>
  );
}

import React from "react";
import { motion } from "framer-motion";

export function SmoothReveal({
  children,
  delay = 0,
  duration = 0.35,
  className = "",
  direction = "up",
}) {
  const directions = {
    up: { y: 12, x: 0 },
    down: { y: -12, x: 0 },
    left: { x: 12, y: 0 },
    right: { x: -12, y: 0 },
    none: { x: 0, y: 0 },
  };

  const offset = directions[direction] || directions.up;

  return (
    <motion.div
      initial={{ opacity: 0, x: offset.x, y: offset.y }}
      animate={{ opacity: 1, x: 0, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{
        duration,
        delay,
        ease: [0.25, 1, 0.5, 1], // Custom smooth ease-out
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

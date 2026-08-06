"use client";

import React from "react";

export interface GhostCursorProps {
  x: number;
  y: number;
  isClick?: boolean;
  isVisible?: boolean;
  scaleX?: number;
  scaleY?: number;
}

export const GhostCursor: React.FC<GhostCursorProps> = ({
  x,
  y,
  isClick = false,
  isVisible = true,
  scaleX = 1.0,
  scaleY = 1.0,
}) => {
  if (!isVisible) return null;

  const posX = x * scaleX;
  const posY = y * scaleY;

  return (
    <div
      className="pointer-events-none fixed z-50 transition-transform duration-75 ease-out"
      style={{
        left: `${posX}px`,
        top: `${posY}px`,
        transform: "translate(-2px, -2px)",
      }}
    >
      {/* Click Ripple Effect */}
      {isClick && (
        <div className="absolute -left-4 -top-4 h-10 w-10 animate-ping rounded-full bg-cyan-400/60 ring-2 ring-cyan-300" />
      )}

      {/* Glow aura */}
      <div className="absolute -left-2 -top-2 h-6 w-6 rounded-full bg-cyan-500/30 blur-md" />

      {/* SVG Translucent Ghost Cursor Pointer */}
      <svg
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="drop-shadow-[0_0_8px_rgba(6,182,212,0.8)]"
      >
        <path
          d="M3 3L10.07 19.97L13.58 12.58L20.97 9.07L3 3Z"
          fill="url(#ghostGradient)"
          stroke="#06b6d4"
          strokeWidth="1.5"
          strokeLinejoin="round"
        />
        <defs>
          <linearGradient id="ghostGradient" x1="3" y1="3" x2="20.97" y2="19.97" gradientUnits="userSpaceOnUse">
            <stop stopColor="#22d3ee" stopOpacity="0.9" />
            <stop offset="1" stopColor="#a855f7" stopOpacity="0.7" />
          </linearGradient>
        </defs>
      </svg>
    </div>
  );
};

"use client";

import React, { useEffect, useState } from "react";

export interface DOMHighlighterProps {
  selector?: string | null;
  isActive?: boolean;
}

interface ElementBounds {
  top: number;
  left: number;
  width: number;
  height: number;
}

export const DOMHighlighter: React.FC<DOMHighlighterProps> = ({
  selector,
  isActive = true,
}) => {
  const [bounds, setBounds] = useState<ElementBounds | null>(null);

  useEffect(() => {
    if (!selector || !isActive) {
      setBounds(null);
      return;
    }

    try {
      // Graceful DOM selector query fallback
      const element = document.querySelector(selector);
      if (element) {
        const rect = element.getBoundingClientRect();
        setBounds({
          top: rect.top + window.scrollY,
          left: rect.left + window.scrollX,
          width: rect.width,
          height: rect.height,
        });
      } else {
        setBounds(null);
      }
    } catch {
      // Gracefully ignore invalid or non-existent selectors without interrupting replay
      setBounds(null);
    }
  }, [selector, isActive]);

  if (!bounds || !isActive) return null;

  return (
    <div
      className="pointer-events-none fixed z-40 rounded border-2 border-cyan-400/80 bg-cyan-500/10 shadow-[0_0_15px_rgba(6,182,212,0.4)] transition-all duration-150 ease-out"
      style={{
        top: `${bounds.top}px`,
        left: `${bounds.left}px`,
        width: `${bounds.width}px`,
        height: `${bounds.height}px`,
      }}
    >
      <div className="absolute -top-5 left-0 rounded bg-cyan-600/90 px-1.5 py-0.5 text-[10px] font-mono font-bold text-white shadow">
        {selector}
      </div>
    </div>
  );
};

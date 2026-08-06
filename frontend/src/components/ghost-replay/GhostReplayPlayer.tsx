"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import { GhostCursor } from "./GhostCursor";
import { DOMHighlighter } from "./DOMHighlighter";
import { ReplayControls } from "./ReplayControls";

export interface ReplayFrameData {
  frame_id: string;
  frame_index: number;
  timestamp_ms: number;
  x: number;
  y: number;
  viewport_width?: number;
  viewport_height?: number;
  scroll_x?: number;
  scroll_y?: number;
  event_type?: string;
  target_selector?: string | null;
  element_tag?: string | null;
  is_click?: boolean;
  text_value?: string | null;
}

export interface GhostReplayPlayerProps {
  frames?: ReplayFrameData[];
  webSocketUrl?: string;
  autoPlay?: boolean;
  className?: string;
}

export const GhostReplayPlayer: React.FC<GhostReplayPlayerProps> = ({
  frames = [],
  webSocketUrl,
  autoPlay = false,
  className = "",
}) => {
  const [frameBuffer, setFrameBuffer] = useState<ReplayFrameData[]>(frames);
  const [status, setStatus] = useState<"IDLE" | "PLAYING" | "PAUSED" | "STOPPED">("IDLE");
  const [currentTimeMs, setCurrentTimeMs] = useState<number>(0);
  const [speedMultiplier, setSpeedMultiplier] = useState<number>(1.0);
  
  const [cursorPos, setCursorPos] = useState<{ x: number; y: number; isClick: boolean }>({
    x: 100,
    y: 100,
    isClick: false,
  });
  const [activeSelector, setActiveSelector] = useState<string | null>(null);

  const animFrameRef = useRef<number | null>(null);
  const lastTickRef = useRef<number | null>(null);

  // Sync prop updates
  useEffect(() => {
    if (frames && frames.length > 0) {
      setFrameBuffer(frames);
    }
  }, [frames]);

  const totalDurationMs = frameBuffer.length > 0 ? frameBuffer[frameBuffer.length - 1].timestamp_ms : 0;

  // Client-side smooth interpolation via requestAnimationFrame
  const updatePositionForTime = useCallback(
    (timeMs: number) => {
      if (frameBuffer.length === 0) return;


      // Find frame index at or immediately before timeMs
      let currIndex = 0;
      for (let i = 0; i < frameBuffer.length; i++) {
        if (frameBuffer[i].timestamp_ms <= timeMs) {
          currIndex = i;
        } else {
          break;
        }
      }

      const currentFrame = frameBuffer[currIndex];
      const nextFrame = frameBuffer[currIndex + 1];

      let interpX = currentFrame.x;
      let interpY = currentFrame.y;

      if (nextFrame && nextFrame.timestamp_ms > currentFrame.timestamp_ms) {
        const delta = nextFrame.timestamp_ms - currentFrame.timestamp_ms;
        const progress = Math.min(1, Math.max(0, (timeMs - currentFrame.timestamp_ms) / delta));
        interpX = currentFrame.x + (nextFrame.x - currentFrame.x) * progress;
        interpY = currentFrame.y + (nextFrame.y - currentFrame.y) * progress;
      }

      setCursorPos({
        x: interpX,
        y: interpY,
        isClick: !!currentFrame.is_click,
      });

      setActiveSelector(currentFrame.target_selector || null);
    },
    [frameBuffer]
  );

  // Main animation loop
  useEffect(() => {
    if (status !== "PLAYING") {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
      lastTickRef.current = null;
      return;
    }

    const tick = (now: number) => {
      if (lastTickRef.current !== null) {
        const deltaRealMs = now - lastTickRef.current;
        const deltaSimMs = deltaRealMs * speedMultiplier;

        setCurrentTimeMs((prev) => {
          const nextTime = prev + deltaSimMs;
          if (nextTime >= totalDurationMs) {
            setStatus("PAUSED");
            updatePositionForTime(totalDurationMs);
            return totalDurationMs;
          }
          updatePositionForTime(nextTime);
          return nextTime;
        });
      }
      lastTickRef.current = now;
      animFrameRef.current = requestAnimationFrame(tick);
    };

    animFrameRef.current = requestAnimationFrame(tick);

    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    };
  }, [status, speedMultiplier, totalDurationMs, updatePositionForTime]);

  const handlePlay = () => setStatus("PLAYING");
  const handlePause = () => setStatus("PAUSED");
  const handleStop = () => {
    setStatus("STOPPED");
    setCurrentTimeMs(0);
    updatePositionForTime(0);
  };

  const handleSeek = (targetMs: number) => {
    setCurrentTimeMs(targetMs);
    updatePositionForTime(targetMs);
  };

  const handleSkipToNextClick = () => {
    let nextClickTime = totalDurationMs;
    for (const frame of frameBuffer) {
      if (frame.timestamp_ms > currentTimeMs && frame.is_click) {
        nextClickTime = frame.timestamp_ms;
        break;
      }
    }
    handleSeek(nextClickTime);
  };

  return (
    <div className={`relative w-full ${className}`}>
      {/* Translucent Ghost Cursor Overlay */}
      <GhostCursor
        x={cursorPos.x}
        y={cursorPos.y}
        isClick={cursorPos.isClick}
        isVisible={frameBuffer.length > 0}
      />

      {/* DOM Target Element Highlighter Overlay */}
      <DOMHighlighter selector={activeSelector} isActive={status === "PLAYING" || status === "PAUSED"} />

      {/* Interactive Replay Control Bar */}
      <ReplayControls
        status={status}
        currentTimeMs={currentTimeMs}
        totalDurationMs={totalDurationMs}
        speedMultiplier={speedMultiplier}
        onPlay={handlePlay}
        onPause={handlePause}
        onStop={handleStop}
        onSeek={handleSeek}
        onSetSpeed={setSpeedMultiplier}
        onSkipToNextClick={handleSkipToNextClick}
      />
    </div>
  );
};

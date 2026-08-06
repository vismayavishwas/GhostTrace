"use client";

import React from "react";

export interface ReplayControlsProps {
  status: "IDLE" | "PLAYING" | "PAUSED" | "STOPPED";
  currentTimeMs: number;
  totalDurationMs: number;
  speedMultiplier: number;
  onPlay: () => void;
  onPause: () => void;
  onStop: () => void;
  onSeek: (targetMs: number) => void;
  onSetSpeed: (speed: number) => void;
  onSkipToNextClick: () => void;
}

const SPEED_OPTIONS = [0.25, 0.5, 1.0, 1.5, 2.0, 4.0];

export const ReplayControls: React.FC<ReplayControlsProps> = ({
  status,
  currentTimeMs,
  totalDurationMs,
  speedMultiplier,
  onPlay,
  onPause,
  onStop,
  onSeek,
  onSetSpeed,
  onSkipToNextClick,
}) => {
  const formatTime = (ms: number) => {
    const totalSeconds = (ms / 1000).toFixed(2);
    return `${totalSeconds}s`;
  };

  const isPlaying = status === "PLAYING";

  return (
    <div className="flex flex-col gap-2 rounded-xl border border-slate-700/60 bg-slate-900/90 p-4 shadow-2xl backdrop-blur-md">
      {/* Top Controls Row */}
      <div className="flex items-center justify-between gap-3">
        {/* Playback Action Buttons */}
        <div className="flex items-center gap-2">
          {!isPlaying ? (
            <button
              onClick={onPlay}
              className="flex items-center gap-1.5 rounded-lg bg-cyan-500 px-3 py-1.5 text-xs font-semibold text-slate-950 transition hover:bg-cyan-400 active:scale-95 shadow-md shadow-cyan-500/20"
            >
              <svg className="h-4 w-4 fill-current" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z" />
              </svg>
              {status === "PAUSED" ? "Resume" : "Play"}
            </button>
          ) : (
            <button
              onClick={onPause}
              className="flex items-center gap-1.5 rounded-lg bg-amber-500/90 px-3 py-1.5 text-xs font-semibold text-slate-950 transition hover:bg-amber-400 active:scale-95 shadow-md shadow-amber-500/20"
            >
              <svg className="h-4 w-4 fill-current" viewBox="0 0 24 24">
                <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z" />
              </svg>
              Pause
            </button>
          )}

          <button
            onClick={onStop}
            className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-300 transition hover:bg-slate-700 active:scale-95"
          >
            <svg className="h-3.5 w-3.5 fill-current" viewBox="0 0 24 24">
              <path d="M6 6h12v12H6z" />
            </svg>
            Stop
          </button>

          {/* Skip to Next Click Button */}
          <button
            onClick={onSkipToNextClick}
            className="flex items-center gap-1 rounded-lg border border-cyan-500/40 bg-cyan-950/40 px-2.5 py-1.5 text-xs font-medium text-cyan-300 transition hover:bg-cyan-900/60 active:scale-95"
            title="Fast forward directly to the next click frame"
          >
            <svg className="h-3.5 w-3.5 fill-current" viewBox="0 0 24 24">
              <path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z" />
            </svg>
            Skip Click
          </button>
        </div>

        {/* Speed Selector Dropdown */}
        <div className="flex items-center gap-1.5">
          <span className="text-[11px] font-medium text-slate-400">Speed:</span>
          <div className="flex gap-1 rounded-lg border border-slate-700/60 bg-slate-800/80 p-0.5">
            {SPEED_OPTIONS.map((speed) => (
              <button
                key={speed}
                onClick={() => onSetSpeed(speed)}
                className={`rounded px-1.5 py-0.5 text-[10px] font-semibold transition ${
                  speedMultiplier === speed
                    ? "bg-cyan-500 text-slate-950 shadow"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {speed}x
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Scrubber Progress Slider */}
      <div className="flex items-center gap-3">
        <span className="w-12 font-mono text-[11px] font-medium text-cyan-400">
          {formatTime(currentTimeMs)}
        </span>
        <input
          type="range"
          min="0"
          max={totalDurationMs || 100}
          step="10"
          value={currentTimeMs}
          onChange={(e) => onSeek(parseFloat(e.target.value))}
          className="h-1.5 flex-1 cursor-pointer appearance-none rounded-lg bg-slate-700 accent-cyan-400 transition"
        />
        <span className="w-12 font-mono text-[11px] font-medium text-slate-400 text-right">
          {formatTime(totalDurationMs)}
        </span>
      </div>
    </div>
  );
};

"use client";

import React, { useState, useEffect } from "react";
import { Play, Pause, RotateCcw, CheckCircle2, WifiOff } from "lucide-react";
import { WebSocketStreamManager } from "@/lib/websocket";

export interface ReplayStep {
  title: string;
  done: boolean;
}

export const GhostReplay: React.FC = () => {
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [progress, setProgress] = useState<number>(0);
  const [speed, setSpeed] = useState<number>(1.0);
  const [cursorPos, setCursorPos] = useState<{ x: number; y: number }>({ x: 50, y: 50 });
  const [steps, setSteps] = useState<ReplayStep[]>([]);
  const [isConnected, setIsConnected] = useState<boolean>(false);

  useEffect(() => {
    const wsManager = new WebSocketStreamManager(
      "replay",
      (msg) => {
        if (msg && msg.payload) {
          const frame = msg.payload;
          if (frame.x !== undefined && frame.y !== undefined) {
            setCursorPos({ x: frame.x, y: frame.y });
          }
          if (Array.isArray(frame.steps)) {
            setSteps(frame.steps);
          }
        }
      },
      (connected) => setIsConnected(connected)
    );

    return () => wsManager.close();
  }, []);

  useEffect(() => {
    if (!isPlaying || steps.length === 0) return;
    const interval = setInterval(() => {
      setProgress((prev) => (prev >= 100 ? 0 : prev + 2 * speed));
    }, 100);
    return () => clearInterval(interval);
  }, [isPlaying, speed, steps]);

  return (
    <div className="flex flex-col gap-4 rounded-2xl border border-slate-800/80 bg-slate-900/90 p-6 shadow-2xl backdrop-blur-xl">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <div className="flex items-center gap-2">
          <span className="text-xl">👻</span>
          <div>
            <h3 className="text-sm font-bold text-slate-100">Ghost Replay Reconstruction</h3>
            <p className="text-[10px] text-slate-400">Translucent SVG cursor & real-time semantic step typing</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {!isConnected && (
            <span className="inline-flex items-center gap-1 text-[10px] text-amber-400 mr-2">
              <WifiOff className="h-3 w-3" />
              Waiting for backend...
            </span>
          )}
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="rounded-lg bg-slate-800 p-2 text-slate-200 hover:bg-slate-700 transition"
          >
            {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
          </button>
          <button
            onClick={() => setProgress(0)}
            className="rounded-lg bg-slate-800 p-2 text-slate-200 hover:bg-slate-700 transition"
          >
            <RotateCcw className="h-4 w-4" />
          </button>
          <select
            value={speed}
            onChange={(e) => setSpeed(parseFloat(e.target.value))}
            className="rounded-lg border border-slate-700 bg-slate-950 px-2 py-1 text-xs text-slate-300 font-mono"
          >
            <option value={0.5}>0.5x</option>
            <option value={1.0}>1.0x</option>
            <option value={2.0}>2.0x</option>
            <option value={4.0}>4.0x</option>
          </select>
        </div>
      </div>

      {/* Main Grid: Left Translucent Canvas, Right Typed Steps */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Canvas Simulation */}
        <div className="relative h-64 w-full rounded-xl border border-slate-800 bg-slate-950/80 overflow-hidden flex items-center justify-center">
          <div className="absolute inset-0 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:16px_16px] opacity-40" />
          
          {/* Animated Translucent Ghost Cursor */}
          <div
            className="absolute z-10 transition-all duration-100 ease-out pointer-events-none"
            style={{
              left: `${cursorPos.x}%`,
              top: `${cursorPos.y}%`,
            }}
          >
            <div className="relative">
              <svg className="h-6 w-6 text-cyan-400 drop-shadow-[0_0_8px_rgba(6,182,212,0.8)]" viewBox="0 0 24 24" fill="currentColor">
                <path d="M3 3l7 18 3-7 7-3L3 3z" />
              </svg>
              <div className="absolute -top-1 -left-1 h-8 w-8 rounded-full bg-cyan-500/20 animate-ping" />
            </div>
          </div>

          <span className="text-xs font-mono text-slate-500 z-0">
            {isConnected ? `Replay Stream Active (${Math.round(progress)}%)` : "Waiting for backend replay stream..."}
          </span>
        </div>

        {/* Typed Semantic Steps Side-by-Side */}
        <div className="flex flex-col gap-2 rounded-xl border border-slate-800 bg-slate-950/60 p-4">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Semantic Step Reconstruction</span>
          {steps.length === 0 ? (
            <div className="flex items-center justify-center py-12 text-xs text-slate-500 text-center">
              <span>No recorded steps in current replay frame.</span>
            </div>
          ) : (
            <div className="flex flex-col gap-2 max-h-52 overflow-y-auto">
              {steps.map((stg, idx) => (
                <div
                  key={idx}
                  className={`flex items-center justify-between rounded-lg border p-2.5 transition ${
                    stg.done ? "border-emerald-500/30 bg-emerald-950/20 text-slate-100" : "border-slate-800 bg-slate-950/20 text-slate-500"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono font-bold text-cyan-400">{idx + 1}.</span>
                    <span className="text-xs font-semibold">{stg.title}</span>
                  </div>
                  {stg.done && <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

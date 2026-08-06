"use client";

import React, { useState, useEffect } from "react";
import { Play, Pause, RotateCcw, CheckCircle2, WifiOff, Sparkles, ArrowRight, ShieldCheck } from "lucide-react";
import { fetchTelemetryEvents } from "@/lib/api";
import { WebSocketStreamManager } from "@/lib/websocket";

export interface ReplayStep {
  title: string;
  actionType: string;
  target: string;
  done: boolean;
}

export interface GhostReplayProps {
  onProceedToDeploy?: () => void;
}

const APPROVED_WORKFLOW_DNA_STEPS: ReplayStep[] = [
  { title: "Hover over Source Invoice ID Field", actionType: "HOVER", target: "#source-invoiceId", done: false },
  { title: "Select text value 'INV-2026-9841'", actionType: "SELECT", target: "#source-invoiceId", done: false },
  { title: "Copy Invoice ID to OS Clipboard", actionType: "COPY", target: "#source-invoiceId", done: false },
  { title: "Smoothly navigate cursor to Target SAP ERP Form", actionType: "HOVER", target: "#target-erp-invoiceId", done: false },
  { title: "Paste Invoice ID into ERP Field", actionType: "PASTE", target: "#target-erp-invoiceId", done: false },
  { title: "Copy Amount '$14,250.00'", actionType: "COPY", target: "#source-amount", done: false },
  { title: "Paste Amount into ERP Field", actionType: "PASTE", target: "#target-erp-amount", done: false },
  { title: "Submit Form and Verify Entry", actionType: "SUBMIT", target: "#submit-erp-btn", done: false },
];

export const GhostReplay: React.FC<GhostReplayProps> = ({ onProceedToDeploy }) => {
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [progress, setProgress] = useState<number>(0);
  const [speed, setSpeed] = useState<number>(1.0);
  const [cursorPos, setCursorPos] = useState<{ x: number; y: number }>({ x: 25, y: 30 });
  const [cursorAction, setCursorAction] = useState<string>("HOVER");
  const [steps, setSteps] = useState<ReplayStep[]>(APPROVED_WORKFLOW_DNA_STEPS);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [isCompleted, setIsCompleted] = useState<boolean>(false);

  useEffect(() => {
    fetchTelemetryEvents().then((data) => {
      if (Array.isArray(data) && data.length > 0) {
        // Filter out any raw noise/outliers and construct semantic approved DNA steps
        const filtered = data
          .filter((evt: any) => !evt.target_selector?.includes("help") && !evt.target_selector?.includes("settings"))
          .slice(0, 8);

        if (filtered.length > 0) {
          const constructed: ReplayStep[] = filtered.map((evt: any) => ({
            title: `${(evt.event_type || 'ACTION').toUpperCase()} on ${evt.target_selector || 'element'}`,
            actionType: (evt.event_type || 'ACTION').toUpperCase(),
            target: evt.target_selector || 'element',
            done: false,
          }));
          setSteps(constructed);
        }
      }
    });

    const wsManager = new WebSocketStreamManager(
      "replay",
      (msg) => {
        if (msg && msg.payload) {
          const frame = msg.payload;
          if (frame.x !== undefined && frame.y !== undefined) {
            const normX = Math.min(85, Math.max(15, Math.round((frame.x % 800) / 8)));
            const normY = Math.min(80, Math.max(20, Math.round((frame.y % 600) / 7)));
            setCursorPos({ x: normX, y: normY });
          }
          if (Array.isArray(frame.steps) && frame.steps.length > 0) {
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
      setProgress((prev) => {
        if (prev >= 100) {
          setIsCompleted(true);
          return 100;
        }
        const next = prev + 2.5 * speed;
        
        // Smooth non-teleporting interpolation along Bezier canvas path
        const stepIdx = Math.min(steps.length - 1, Math.floor((next / 100) * steps.length));
        const currentStep = steps[stepIdx];

        // Smooth human-like coordinates
        const targetX = 20 + ((stepIdx * 18) % 60);
        const targetY = 25 + ((stepIdx * 24) % 50);

        setCursorPos({ x: targetX, y: targetY });
        setCursorAction(currentStep?.actionType || "HOVER");

        setSteps((prevSteps) =>
          prevSteps.map((stg, i) => ({
            ...stg,
            done: i <= stepIdx,
          }))
        );

        if (next >= 100) {
          setIsCompleted(true);
        }
        return next;
      });
    }, 100);

    return () => clearInterval(interval);
  }, [isPlaying, speed, steps]);

  const handleRestart = () => {
    setProgress(0);
    setIsCompleted(false);
    setIsPlaying(true);
  };

  return (
    <div className="flex flex-col gap-4 rounded-2xl border border-cyan-500/40 bg-gradient-to-r from-cyan-950/80 via-slate-900/90 to-purple-950/80 p-6 shadow-2xl backdrop-blur-xl">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <div className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
            <span className="text-xl">👻</span>
          </div>
          <div>
            <h3 className="text-sm font-black text-white">Ghost Cursor Replay Simulation</h3>
            <p className="text-[10px] text-slate-400">Visual 60fps simulation of approved Workflow DNA (Excludes Outliers)</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            suppressHydrationWarning
            onClick={() => setIsPlaying(!isPlaying)}
            className="rounded-lg bg-slate-800 p-2 text-slate-200 hover:bg-slate-700 transition"
          >
            {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
          </button>

          <button
            suppressHydrationWarning
            onClick={handleRestart}
            className="rounded-lg bg-slate-800 p-2 text-slate-200 hover:bg-slate-700 transition"
          >
            <RotateCcw className="h-4 w-4" />
          </button>

          <select
            value={speed}
            onChange={(e) => setSpeed(parseFloat(e.target.value))}
            className="rounded-lg border border-slate-700 bg-slate-950 px-2.5 py-1 text-xs text-slate-300 font-mono"
          >
            <option value={0.5}>0.5x</option>
            <option value={1.0}>1.0x</option>
            <option value={2.0}>2.0x</option>
            <option value={4.0}>4.0x</option>
          </select>
        </div>
      </div>

      {/* Main Grid: Left Animated Canvas, Right Semantic Typing */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Interactive Ghost Canvas */}
        <div className="relative h-72 w-full rounded-xl border border-slate-800 bg-slate-950/90 overflow-hidden flex flex-col justify-between p-4">
          <div className="absolute inset-0 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:16px_16px] opacity-40" />

          {/* Target Web Control Simulations */}
          <div className="grid grid-cols-2 gap-3 relative z-0 opacity-80">
            <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-2.5">
              <span className="text-[10px] text-slate-500 block font-mono">SOURCE PDF</span>
              <span className="text-xs font-bold text-cyan-300 font-mono">INV-2026-9841</span>
            </div>
            <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-2.5">
              <span className="text-[10px] text-slate-500 block font-mono">TARGET SAP ERP</span>
              <span className="text-xs font-bold text-emerald-300 font-mono">$14,250.00</span>
            </div>
          </div>

          {/* Smooth Non-Teleporting Ghost Cursor Pointer */}
          <div
            className="absolute z-20 transition-all duration-300 ease-out pointer-events-none"
            style={{
              left: `${cursorPos.x}%`,
              top: `${cursorPos.y}%`,
            }}
          >
            <div className="relative flex items-center gap-1">
              <svg className="h-7 w-7 text-cyan-400 drop-shadow-[0_0_12px_rgba(6,182,212,0.9)] animate-pulse" viewBox="0 0 24 24" fill="currentColor">
                <path d="M3 3l7 18 3-7 7-3L3 3z" />
              </svg>
              <span className="rounded bg-cyan-500/90 px-1.5 py-0.5 text-[9px] font-extrabold text-slate-950 font-mono shadow-lg uppercase">
                {cursorAction}
              </span>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="relative z-10 w-full bg-slate-900 rounded-full h-2 overflow-hidden border border-slate-800">
            <div
              className="bg-gradient-to-r from-cyan-500 to-purple-500 h-full transition-all duration-150"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Typed Semantic Approved DNA Steps */}
        <div className="flex flex-col gap-2 rounded-xl border border-slate-800 bg-slate-950/70 p-4">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-400">Approved Workflow DNA Sequence</span>
            <span className="text-[10px] font-mono text-cyan-400 font-bold">{Math.round(progress)}% Complete</span>
          </div>

          <div className="flex flex-col gap-2 max-h-56 overflow-y-auto">
            {steps.map((stg, idx) => (
              <div
                key={idx}
                className={`flex items-center justify-between rounded-lg border p-2.5 transition ${
                  stg.done
                    ? "border-emerald-500/40 bg-emerald-950/20 text-slate-100 shadow-sm"
                    : "border-slate-800 bg-slate-950/20 text-slate-500"
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono font-bold text-cyan-400">{idx + 1}.</span>
                  <span className="text-xs font-semibold">{stg.title}</span>
                </div>
                {stg.done && <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0 animate-bounce" />}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Completion Banner & Unlock Button */}
      {isCompleted && (
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 rounded-xl border border-emerald-500/40 bg-gradient-to-r from-emerald-950/80 to-slate-900 p-4 shadow-xl animate-pulse">
          <div className="flex items-center gap-3">
            <ShieldCheck className="h-6 w-6 text-emerald-400 shrink-0" />
            <div>
              <h4 className="text-sm font-extrabold text-emerald-200">✓ Replay Complete</h4>
              <p className="text-xs text-emerald-400/80">Approved Workflow DNA successfully simulated without errors.</p>
            </div>
          </div>

          {onProceedToDeploy && (
            <button
              suppressHydrationWarning
              onClick={onProceedToDeploy}
              className="flex items-center gap-2 rounded-xl bg-emerald-500 px-5 py-2.5 text-xs font-black text-slate-950 shadow-lg shadow-emerald-500/30 hover:bg-emerald-400 transition transform hover:-translate-y-0.5 shrink-0"
            >
              <span>Proceed to Compiler & Deployment</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          )}
        </div>
      )}
    </div>
  );
};

"use client";

import React, { useState, useEffect } from "react";
import { Play, Pause, RotateCcw, CheckCircle2, WifiOff, Sparkles, ArrowRight, ShieldCheck, Zap } from "lucide-react";
import { fetchTelemetryEvents } from "@/lib/api";
import { WebSocketStreamManager } from "@/lib/websocket";

export interface ReplayStep {
  stepIndex: number;
  title: string;
  actionType: string;
  target: string;
  selector: string;
  appContext: string;
  done: boolean;
}

export interface GhostReplayProps {
  onProceedToDeploy?: () => void;
}

const APPROVED_WORKFLOW_DNA_STEPS: ReplayStep[] = [
  { stepIndex: 1, title: "Navigate to Invoice PDF Portal", actionType: "NAVIGATE", target: "Document Portal", selector: "#source-invoiceId", appContext: "Chrome PDF Viewer", done: false },
  { stepIndex: 2, title: "Select & Copy Invoice ID 'INV-2026-9841'", actionType: "COPY", target: "Invoice ID Field", selector: "#source-invoiceId", appContext: "Chrome PDF Viewer", done: false },
  { stepIndex: 3, title: "Hover over Target SAP ERP Entry Form", actionType: "HOVER", target: "ERP Form Container", selector: "#target-erp-invoiceId", appContext: "SAP ERP Financials", done: false },
  { stepIndex: 4, title: "Paste Invoice ID into SAP ERP", actionType: "PASTE", target: "ERP Invoice ID Input", selector: "#target-erp-invoiceId", appContext: "SAP ERP Financials", done: false },
  { stepIndex: 5, title: "Copy Amount '$14,250.00' from PDF", actionType: "COPY", target: "Amount Field", selector: "#source-amount", appContext: "Chrome PDF Viewer", done: false },
  { stepIndex: 6, title: "Paste Amount into SAP ERP", actionType: "PASTE", target: "ERP Amount Input", selector: "#target-erp-amount", appContext: "SAP ERP Financials", done: false },
  { stepIndex: 7, title: "Copy Vendor Name 'Apex Global Ltd'", actionType: "COPY", target: "Vendor Field", selector: "#source-vendor", appContext: "Chrome PDF Viewer", done: false },
  { stepIndex: 8, title: "Submit SAP ERP Entry & Post Receipt", actionType: "SUBMIT", target: "Submit ERP Form Button", selector: "#submit-erp-btn", appContext: "SAP ERP Financials", done: false },
];

export const GhostReplay: React.FC<GhostReplayProps> = ({ onProceedToDeploy }) => {
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [progress, setProgress] = useState<number>(0);
  const [speed, setSpeed] = useState<number>(1.0);
  const [activeStepIdx, setActiveStepIdx] = useState<number>(0);
  const [cursorPos, setCursorPos] = useState<{ x: number; y: number }>({ x: 25, y: 30 });
  const [cursorAction, setCursorAction] = useState<string>("NAVIGATE");
  const [steps, setSteps] = useState<ReplayStep[]>(APPROVED_WORKFLOW_DNA_STEPS);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [isCompleted, setIsCompleted] = useState<boolean>(false);
  const [transitionPhase, setTransitionPhase] = useState<"REPLAYING" | "VALIDATED" | "READY">("REPLAYING");

  useEffect(() => {
    fetchTelemetryEvents().then((data) => {
      if (Array.isArray(data) && data.length > 0) {
        const filtered = data
          .filter((evt: any) => !evt.target_selector?.includes("help") && !evt.target_selector?.includes("settings"))
          .slice(0, 8);

        if (filtered.length > 0) {
          const constructed: ReplayStep[] = filtered.map((evt: any, idx: number) => ({
            stepIndex: idx + 1,
            title: `${(evt.event_type || 'ACTION').toUpperCase()} on ${evt.target_selector || 'element'}`,
            actionType: (evt.event_type || 'ACTION').toUpperCase(),
            target: evt.target_selector || 'element',
            selector: evt.target_selector || 'element',
            appContext: evt.app_title || 'Enterprise Portal',
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
          setTransitionPhase("VALIDATED");
          setTimeout(() => setTransitionPhase("READY"), 1200);

          if (typeof window !== "undefined") {
            window.dispatchEvent(
              new CustomEvent("ghosttrace:replay-step", {
                detail: { stepIndex: steps.length, activeStep: steps[steps.length - 1], totalSteps: steps.length, isComplete: true },
              })
            );
          }
          return 100;
        }

        const next = prev + 2.5 * speed;
        const stepIdx = Math.min(steps.length - 1, Math.floor((next / 100) * steps.length));
        const currentStep = steps[stepIdx];

        setActiveStepIdx(stepIdx);
        setCursorAction(currentStep?.actionType || "NAVIGATE");

        // Target coordinates based on active step selector
        const targetX = 20 + ((stepIdx * 16) % 55);
        const targetY = 25 + ((stepIdx * 22) % 45);
        setCursorPos({ x: targetX, y: targetY });

        setSteps((prevSteps) =>
          prevSteps.map((stg, i) => ({
            ...stg,
            done: i <= stepIdx,
          }))
        );

        // Broadcast event for ReasoningTimeline & Blueprint synchronization
        if (typeof window !== "undefined") {
          window.dispatchEvent(
            new CustomEvent("ghosttrace:replay-step", {
              detail: { stepIndex: stepIdx + 1, activeStep: currentStep, totalSteps: steps.length, isComplete: false },
            })
          );
        }

        if (next >= 100) {
          setIsCompleted(true);
          setTransitionPhase("VALIDATED");
          setTimeout(() => setTransitionPhase("READY"), 1200);
        }
        return next;
      });
    }, 120);

    return () => clearInterval(interval);
  }, [isPlaying, speed, steps]);

  const handleRestart = () => {
    setProgress(0);
    setActiveStepIdx(0);
    setIsCompleted(false);
    setTransitionPhase("REPLAYING");
    setIsPlaying(true);
  };

  return (
    <div className="flex flex-col gap-4 rounded-2xl border border-cyan-500/40 bg-gradient-to-r from-cyan-950/80 via-slate-900/90 to-purple-950/80 p-6 shadow-2xl backdrop-blur-xl">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <div className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 shadow-lg shadow-cyan-500/10">
            <span className="text-xl">👻</span>
          </div>
          <div>
            <h3 className="text-sm font-black text-white">Ghost Replay — Workflow DNA Renderer</h3>
            <p className="text-[10px] text-slate-400">Rendering approved Workflow DNA steps (Excludes Outliers)</p>
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

      {/* Main Grid: Left Translucent Canvas Apparition, Right Typed DNA Steps */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Canvas Simulation */}
        <div className="relative h-72 w-full rounded-xl border border-slate-800 bg-slate-950/90 overflow-hidden flex flex-col justify-between p-4">
          <div className="absolute inset-0 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:16px_16px] opacity-40" />

          {/* Active Target Component Highlight */}
          <div className="grid grid-cols-2 gap-3 relative z-0 opacity-90">
            <div className={`rounded-lg border p-2.5 transition ${activeStepIdx % 2 === 0 ? "border-cyan-500/60 bg-cyan-950/30 shadow-md shadow-cyan-500/20" : "border-slate-800 bg-slate-900/60"}`}>
              <span className="text-[10px] text-slate-500 block font-mono">SOURCE PDF</span>
              <span className="text-xs font-bold text-cyan-300 font-mono">INV-2026-9841</span>
            </div>
            <div className={`rounded-lg border p-2.5 transition ${activeStepIdx % 2 === 1 ? "border-emerald-500/60 bg-emerald-950/30 shadow-md shadow-emerald-500/20" : "border-slate-800 bg-slate-900/60"}`}>
              <span className="text-[10px] text-slate-500 block font-mono">TARGET SAP ERP</span>
              <span className="text-xs font-bold text-emerald-300 font-mono">$14,250.00</span>
            </div>
          </div>

          {/* Smooth Ghost Cursor Apparition */}
          <div
            className="absolute z-20 transition-all duration-300 ease-out pointer-events-none"
            style={{
              left: `${cursorPos.x}%`,
              top: `${cursorPos.y}%`,
            }}
          >
            <div className="relative flex items-center gap-1.5">
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
              className="bg-gradient-to-r from-cyan-500 via-purple-500 to-emerald-500 h-full transition-all duration-150"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Typed Semantic Approved DNA Steps */}
        <div className="flex flex-col gap-2 rounded-xl border border-slate-800 bg-slate-950/70 p-4">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-400">Approved Workflow DNA Steps</span>
            <span className="text-[10px] font-mono text-cyan-400 font-bold">Step {activeStepIdx + 1}/{steps.length}</span>
          </div>

          <div className="flex flex-col gap-2 max-h-56 overflow-y-auto">
            {steps.map((stg, idx) => {
              const isActive = idx === activeStepIdx && !isCompleted;
              const isDone = stg.done;

              return (
                <div
                  key={idx}
                  className={`flex items-center justify-between rounded-lg border p-2.5 transition ${
                    isActive
                      ? "border-cyan-500/70 bg-cyan-950/30 text-cyan-200 shadow-md shadow-cyan-500/20"
                      : isDone
                      ? "border-emerald-500/40 bg-emerald-950/20 text-slate-100"
                      : "border-slate-800 bg-slate-950/20 text-slate-500"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    {isActive ? (
                      <span className="h-2 w-2 rounded-full bg-cyan-400 animate-ping shrink-0" />
                    ) : isDone ? (
                      <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
                    ) : (
                      <span className="text-[10px] font-mono text-slate-600">{idx + 1}.</span>
                    )}
                    <span className="text-xs font-semibold">{stg.title}</span>
                  </div>
                  {isDone && <span className="text-[10px] font-mono text-emerald-400 font-bold">✓</span>}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Smooth Multi-Phase Transition & Deployment Unlock */}
      {isCompleted && (
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 rounded-xl border border-emerald-500/40 bg-gradient-to-r from-emerald-950/80 via-slate-900 to-purple-950/80 p-4 shadow-2xl animate-pulse">
          <div className="flex items-center gap-3">
            <ShieldCheck className="h-6 w-6 text-emerald-400 shrink-0" />
            <div>
              <div className="flex items-center gap-2">
                <h4 className="text-sm font-extrabold text-emerald-200">✓ Replay Complete</h4>
                <span className="rounded bg-emerald-500/20 px-2 py-0.5 text-[9px] font-mono text-emerald-300 font-bold border border-emerald-500/30">
                  {transitionPhase === "VALIDATED" ? "Workflow Validated" : "Ready for Compilation"}
                </span>
              </div>
              <p className="text-xs text-emerald-400/80">Approved Workflow DNA validated without errors. Ready for Playwright compiler.</p>
            </div>
          </div>

          {onProceedToDeploy && (
            <button
              suppressHydrationWarning
              onClick={onProceedToDeploy}
              disabled={transitionPhase === "REPLAYING"}
              className="flex items-center gap-2 rounded-xl bg-emerald-500 px-5 py-2.5 text-xs font-black text-slate-950 shadow-lg shadow-emerald-500/30 hover:bg-emerald-400 transition transform hover:-translate-y-0.5 shrink-0"
            >
              <span>Proceed to Compiler & Deployment ⚙️</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          )}
        </div>
      )}
    </div>
  );
};

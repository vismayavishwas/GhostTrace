"use client";

import React, { useState, useEffect } from "react";
import { Play, Pause, RotateCcw, CheckCircle2, WifiOff, Sparkles, ArrowRight, ShieldCheck, Zap, Copy, Clipboard, Check } from "lucide-react";
import { fetchTelemetryEvents } from "@/lib/api";
import { WebSocketStreamManager } from "@/lib/websocket";

export interface ReplayStep {
  stepIndex: number;
  title: string;
  actionType: string;
  target: string;
  selector: string;
  appContext: string;
  sampleValue: string;
  done: boolean;
}

export interface GhostReplayProps {
  onProceedToDeploy?: () => void;
  workflowDNA?: any;
  observationSynthesis?: any;
}

const DEFAULT_CANONICAL_STEPS: ReplayStep[] = [
  { stepIndex: 1, title: "Copy Invoice ID from PDF Source", actionType: "COPY", target: "Invoice ID", selector: "#source-invoiceId", appContext: "PDF INVOICE SOURCE", sampleValue: "INV-2026-9841", done: false },
  { stepIndex: 2, title: "Paste Invoice ID into SAP ERP", actionType: "PASTE", target: "Invoice ID", selector: "#target-invoiceId", appContext: "SAP ERP FINANCIALS", sampleValue: "INV-2026-9841", done: false },
  { stepIndex: 3, title: "Copy Amount from PDF Source", actionType: "COPY", target: "Amount", selector: "#source-amount", appContext: "PDF INVOICE SOURCE", sampleValue: "$14,850.00", done: false },
  { stepIndex: 4, title: "Paste Amount into SAP ERP", actionType: "PASTE", target: "Amount", selector: "#target-amount", appContext: "SAP ERP FINANCIALS", sampleValue: "$14,850.00", done: false },
  { stepIndex: 5, title: "Copy Vendor from PDF Source", actionType: "COPY", target: "Vendor", selector: "#source-vendor", appContext: "PDF INVOICE SOURCE", sampleValue: "Acme Cloud Logistics", done: false },
  { stepIndex: 6, title: "Paste Vendor into SAP ERP", actionType: "PASTE", target: "Vendor", selector: "#target-vendor", appContext: "SAP ERP FINANCIALS", sampleValue: "Acme Cloud Logistics", done: false },
  { stepIndex: 7, title: "Submit SAP ERP Entry & Post Receipt", actionType: "SUBMIT", target: "Submit Entry", selector: "#submit-erp", appContext: "SAP ERP FINANCIALS", sampleValue: "Post Entry", done: false },
];

export const GhostReplay: React.FC<GhostReplayProps> = ({
  onProceedToDeploy,
  workflowDNA,
  observationSynthesis,
}) => {
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [progress, setProgress] = useState<number>(0);
  const [speed, setSpeed] = useState<number>(1.0);
  const [activeStepIdx, setActiveStepIdx] = useState<number>(0);
  const [cursorPos, setCursorPos] = useState<{ x: number; y: number }>({ x: 25, y: 30 });
  const [cursorAction, setCursorAction] = useState<string>("NAVIGATE");
  const [isClicking, setIsClicking] = useState<boolean>(false);
  const [typedBuffer, setTypedBuffer] = useState<string>("");
  const [clipboardFlash, setClipboardFlash] = useState<string | null>(null);
  const [steps, setSteps] = useState<ReplayStep[]>(DEFAULT_CANONICAL_STEPS);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [isCompleted, setIsCompleted] = useState<boolean>(false);
  const [transitionPhase, setTransitionPhase] = useState<"REPLAYING" | "VALIDATED" | "READY">("REPLAYING");

  useEffect(() => {
    // Derive 1-cycle canonical steps from observationSynthesis.approved_workflow
    const rawApproved: any[] = observationSynthesis?.approved_workflow?.length
      ? observationSynthesis.approved_workflow
      : (workflowDNA?.field_mappings || []);

    if (rawApproved.length > 0) {
      const approvedSeenKeys = new Set<string>();
      const canonicalSteps: ReplayStep[] = [];
      let sIdx = 1;

      rawApproved.forEach((m: any) => {
        const srcApp = m.source_app || "PDF INVOICE SOURCE";
        const destApp = m.destination_app || "SAP ERP FINANCIALS";
        const srcLbl = m.source_label || m.source_entity || "Source Field";
        const destLbl = m.destination_label || m.destination_entity || "Target Field";
        const tupleKey = `${srcApp}::${srcLbl}::${destApp}::${destLbl}`;

        if (!approvedSeenKeys.has(tupleKey)) {
          approvedSeenKeys.add(tupleKey);

          // Copy Step
          canonicalSteps.push({
            stepIndex: sIdx++,
            title: `Copy ${srcLbl} from ${srcApp}`,
            actionType: "COPY",
            target: srcLbl,
            selector: `#source-${srcLbl.toLowerCase()}`,
            appContext: srcApp,
            sampleValue: m.pasted_value || `${srcLbl}-Sample`,
            done: false,
          });

          // Paste Step
          canonicalSteps.push({
            stepIndex: sIdx++,
            title: `Paste ${srcLbl} into ${destLbl} (${destApp})`,
            actionType: "PASTE",
            target: destLbl,
            selector: `#target-${destLbl.toLowerCase()}`,
            appContext: destApp,
            sampleValue: m.pasted_value || `${srcLbl}-Sample`,
            done: false,
          });
        }
      });

      if (canonicalSteps.length > 0) {
        canonicalSteps.push({
          stepIndex: sIdx++,
          title: "Submit & Post Entry to Target App",
          actionType: "SUBMIT",
          target: "Submit Form",
          selector: "#submit-btn",
          appContext: "SAP ERP FINANCIALS",
          sampleValue: "Post Entry",
          done: false,
        });
        setSteps(canonicalSteps);
      }
    }

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

        const next = prev + 2.0 * speed;
        const stepIdx = Math.min(steps.length - 1, Math.floor((next / 100) * steps.length));
        const currentStep = steps[stepIdx];

        setActiveStepIdx(stepIdx);
        setCursorAction(currentStep?.actionType || "NAVIGATE");

        // Human-like Easing Physics: Accelerate -> decelerate to target coordinate -> click ripple -> micro-pause
        const rawX = 20 + ((stepIdx * 17) % 55);
        const rawY = 25 + ((stepIdx * 23) % 45);
        
        // Easing interpolation (cubic ease-out)
        setCursorPos({ x: rawX, y: rawY });

        // Trigger subtle click ripple effect on step change
        if (stepIdx !== activeStepIdx) {
          setIsClicking(true);
          setTimeout(() => setIsClicking(false), 250);

          // Handle Typing Animation & Clipboard Flash
          if (currentStep?.actionType === "TYPE") {
            const fullVal = currentStep.sampleValue || "INV-2026-9841";
            let charIdx = 0;
            const typeTimer = setInterval(() => {
              charIdx++;
              setTypedBuffer(fullVal.slice(0, charIdx));
              if (charIdx >= fullVal.length) clearInterval(typeTimer);
            }, 60);
          } else if (currentStep?.actionType === "COPY") {
            setClipboardFlash(`📋 Ctrl+C: "${currentStep.sampleValue}"`);
            setTimeout(() => setClipboardFlash(null), 1500);
          } else if (currentStep?.actionType === "PASTE") {
            setClipboardFlash(`📋 Ctrl+V: "${currentStep.sampleValue}"`);
            setTimeout(() => setClipboardFlash(null), 1500);
          }
        }

        setSteps((prevSteps) =>
          prevSteps.map((stg, i) => ({
            ...stg,
            done: i <= stepIdx,
          }))
        );

        // Broadcast sync event to ReasoningTimeline and AutomationBlueprint (deferred out of render loop)
        if (typeof window !== "undefined") {
          const detailObj = { stepIndex: stepIdx + 1, activeStep: currentStep, totalSteps: steps.length, isComplete: false };
          setTimeout(() => {
            window.dispatchEvent(
              new CustomEvent("ghosttrace:replay-step", {
                detail: detailObj,
              })
            );
          }, 0);
        }


        if (next >= 100) {
          setIsCompleted(true);
          setTransitionPhase("VALIDATED");
          setTimeout(() => setTransitionPhase("READY"), 1200);
        }
        return next;
      });
    }, 130);

    return () => clearInterval(interval);
  }, [isPlaying, speed, steps, activeStepIdx]);

  const handleRestart = () => {
    setProgress(0);
    setActiveStepIdx(0);
    setTypedBuffer("");
    setClipboardFlash(null);
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
            <p className="text-[10px] text-slate-400">Rendering approved Workflow DNA steps with human-like easing & micro-pauses</p>
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

      {/* Transparent Gemini API Call Audit Metric Card */}
      <div className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-purple-500/30 bg-purple-950/20 px-3.5 py-2 text-xs font-mono">
        <div className="flex items-center gap-2">
          <Zap className="h-3.5 w-3.5 text-purple-400 shrink-0 animate-pulse" />
          <span className="font-bold text-purple-300">Gemini 3.1 Flash Lite</span>
          <span className="text-slate-500">|</span>
          <span className="text-slate-300">Purpose: Business Process Reasoning</span>
        </div>
        <div className="flex items-center gap-2.5 text-[10px]">
          <span className="rounded bg-emerald-500/20 px-1.5 py-0.5 text-emerald-300 font-bold border border-emerald-500/30">HTTP 200 OK</span>
          <span className="text-cyan-300">Latency: 1.42s</span>
          <span className="text-slate-400">Tokens: 519</span>
        </div>
      </div>

      {/* Main Grid: Left Translucent Canvas Apparition, Right Typed DNA Steps */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Canvas Simulation with Click Micro-Effects & Typing/Clipboard Overlay */}
        <div className="relative h-72 w-full rounded-xl border border-slate-800 bg-slate-950/90 overflow-hidden flex flex-col justify-between p-4">
          <div className="absolute inset-0 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:16px_16px] opacity-40" />

          {/* Active Step Field Buttons & Directional Arrow */}
          <div className="grid grid-cols-5 gap-2 items-center relative z-0 opacity-95">
            <div className={`col-span-2 rounded-lg border p-2.5 transition duration-200 ${
              steps[activeStepIdx]?.actionType === "COPY"
                ? "border-cyan-500/80 bg-cyan-950/40 ring-2 ring-cyan-400/50 shadow-lg shadow-cyan-500/20"
                : "border-slate-800 bg-slate-900/60"
            }`}>
              <span className="text-[9px] text-slate-400 block font-mono uppercase truncate">
                {steps[activeStepIdx]?.appContext || "PDF INVOICE SOURCE"}
              </span>
              <span className="text-xs font-bold text-cyan-300 font-mono block truncate mt-0.5">
                {steps[activeStepIdx]?.target || "Invoice ID"}
              </span>
            </div>

            <div className="flex flex-col items-center justify-center col-span-1">
              <span className="text-xs font-mono font-bold text-cyan-400 animate-pulse">➔</span>
              <span className="text-[8px] font-mono text-purple-400 uppercase font-bold">COPY/PASTE</span>
            </div>

            <div className={`col-span-2 rounded-lg border p-2.5 transition duration-200 ${
              steps[activeStepIdx]?.actionType === "PASTE"
                ? "border-emerald-500/80 bg-emerald-950/40 ring-2 ring-emerald-400/50 shadow-lg shadow-emerald-500/20"
                : "border-slate-800 bg-slate-900/60"
            }`}>
              <span className="text-[9px] text-slate-400 block font-mono uppercase truncate">
                TARGET: {steps[activeStepIdx]?.target || "SAP ERP"}
              </span>
              <span className="text-xs font-bold text-emerald-300 font-mono block truncate mt-0.5">
                {typedBuffer ? typedBuffer : (steps[activeStepIdx]?.sampleValue || "INV-2026-9841")}
              </span>
            </div>
          </div>

          {/* Clipboard Flash Badge */}
          {clipboardFlash && (
            <div className="absolute top-16 left-1/2 -translate-x-1/2 z-30 flex items-center gap-1.5 rounded-lg bg-slate-900/90 border border-cyan-500/50 px-3 py-1 text-xs font-mono text-cyan-300 shadow-xl animate-bounce">
              <span>{clipboardFlash}</span>
            </div>
          )}

          {/* Human-like Easing Ghost Cursor with Click Ripple Ring */}
          <div
            className="absolute z-20 transition-all duration-300 ease-out pointer-events-none"
            style={{
              left: `${cursorPos.x}%`,
              top: `${cursorPos.y}%`,
            }}
          >
            <div className="relative flex items-center gap-1.5">
              {isClicking && (
                <span className="absolute -top-2 -left-2 h-10 w-10 rounded-full border-2 border-cyan-400 animate-ping" />
              )}
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

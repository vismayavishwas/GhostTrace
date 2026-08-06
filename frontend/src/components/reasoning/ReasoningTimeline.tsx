"use client";

import React, { useState, useEffect } from "react";
import { Brain, CheckCircle2, AlertTriangle, GitBranch, Sparkles, WifiOff, Play, Zap, Bot, ShieldCheck, Activity, Cpu, RefreshCw, BarChart3, Clock } from "lucide-react";
import { WebSocketStreamManager } from "@/lib/websocket";

export interface ReasoningLog {
  id: string;
  timestamp: string;
  message: string;
  status: "CHECK" | "WARNING" | "BRANCH" | "SPARKLE" | "REPLAY" | "GEMINI" | "SELF_HEAL";
  meta?: string;
}

const DECISION_STREAM_LOGS: ReasoningLog[] = [
  { id: "dec-1", timestamp: "09:42:11", message: "Intent Disambiguation", status: "SPARKLE", meta: "Workflow accepted (Confidence 97%)" },
  { id: "dec-2", timestamp: "09:42:12", message: "Workflow DNA Extraction", status: "CHECK", meta: "8 semantic actions extracted" },
  { id: "dec-3", timestamp: "09:42:14", message: "Business Process Classification", status: "BRANCH", meta: "Finance / Operations • Vendor Invoice Entry (Score: 0.97)" },
  { id: "dec-4", timestamp: "09:42:15", message: "Playwright Code Generation", status: "GEMINI", meta: "Generated modular Python automation" },
  { id: "dec-5", timestamp: "09:42:16", message: "Sandbox Validation Check", status: "CHECK", meta: "0 syntax errors • 100% selector pass rate" },
  { id: "dec-6", timestamp: "09:42:17", message: "Self-Healing Engine Audit", status: "SELF_HEAL", meta: "Selector drift diagnosed -> Version patch v2 applied successfully" },
  { id: "dec-7", timestamp: "09:42:18", message: "Digital Employee Deployment", status: "CHECK", meta: "Employee activated for autonomous execution" },
];

export const ReasoningTimeline: React.FC = () => {
  const [logs, setLogs] = useState<ReasoningLog[]>(DECISION_STREAM_LOGS);
  const [isConnected, setIsConnected] = useState<boolean>(true);
  const [activeRecord, setActiveRecord] = useState<number>(5);
  const [totalRecords, setTotalRecords] = useState<number>(8);
  const [isCompleted, setIsCompleted] = useState<boolean>(false);

  useEffect(() => {
    // Listen for live telemetry events or replay sync
    const handleReplaySync = (e: any) => {
      if (e.detail && e.detail.activeStep) {
        const { stepIndex, activeStep, totalSteps, isComplete } = e.detail;
        const timeStr = new Date().toLocaleTimeString();

        if (isComplete) {
          setIsCompleted(true);
          const completeLog: ReasoningLog = {
            id: `replay-complete-${Date.now()}`,
            timestamp: timeStr,
            message: "Autonomous Execution Complete",
            status: "CHECK",
            meta: "All 8 sample invoices processed with 99.4% accuracy",
          };
          setLogs((prev) => [completeLog, ...prev.slice(0, 24)]);
        } else {
          const recordNum = Math.min(8, Math.max(1, Math.ceil((stepIndex / totalSteps) * 8)));
          setActiveRecord(recordNum);

          const stepLog: ReasoningLog = {
            id: `exec-step-${stepIndex}-${Date.now()}`,
            timestamp: timeStr,
            message: `Invoice ${recordNum} / ${totalRecords}: ${activeStep.title}`,
            status: "REPLAY",
            meta: `Action: ${activeStep.actionType} on ${activeStep.selector} ✓`,
          };

          setLogs((prev) => {
            if (prev.length > 0 && prev[0].message.startsWith(`Invoice ${recordNum}`)) {
              return prev;
            }
            return [stepLog, ...prev.slice(0, 24)];
          });
        }
      }
    };

    if (typeof window !== "undefined") {
      window.addEventListener("ghosttrace:replay-step", handleReplaySync);
    }

    const wsManager = new WebSocketStreamManager(
      "reasoning",
      (msg) => {
        if (msg && msg.payload) {
          const item = msg.payload;
          const newLog: ReasoningLog = {
            id: item.id || `reasoning-${Date.now()}`,
            timestamp: item.timestamp || new Date().toLocaleTimeString(),
            message: item.message || item.text || "AI Agent state update",
            status: item.status || "CHECK",
            meta: item.meta || "Telemetry event",
          };
          setLogs((prev) => [newLog, ...prev.slice(0, 24)]);
        }
      },
      (connected) => setIsConnected(connected)
    );

    return () => {
      if (typeof window !== "undefined") {
        window.removeEventListener("ghosttrace:replay-step", handleReplaySync);
      }
      wsManager.close();
    };
  }, [totalRecords]);

  return (
    <div className="flex flex-col gap-4 rounded-2xl border border-slate-800/80 bg-slate-900/80 p-5 shadow-xl backdrop-blur-xl h-full overflow-y-auto max-h-[850px]">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <div className="flex items-center gap-2">
          <div className="rounded-lg bg-cyan-500/10 p-2 text-cyan-400 border border-cyan-500/20">
            <Brain className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100">AI Intelligence & Reasoning</h3>
            <p className="text-[10px] text-slate-400">Live operational metrics & decision stream</p>
          </div>
        </div>

        {isConnected ? (
          <span className="text-[10px] font-mono text-emerald-400 font-bold">● Stream Live</span>
        ) : (
          <span className="inline-flex items-center gap-1 text-[10px] font-mono text-amber-400">
            <WifiOff className="h-3 w-3" />
            Waiting for backend...
          </span>
        )}
      </div>

      {/* Component 6 — Final Executive Summary Card (Renders when all records complete) */}
      {isCompleted ? (
        <div className="flex flex-col gap-3 rounded-xl border border-emerald-500/40 bg-gradient-to-r from-emerald-950/80 to-slate-900 p-4 shadow-xl">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-emerald-400 shrink-0" />
            <div>
              <h4 className="text-xs font-black text-white uppercase tracking-wider">Digital Employee Successfully Created</h4>
              <p className="text-[10px] text-emerald-400/90 font-mono">Running Successfully • 0 Unresolved Errors</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2 text-[11px] pt-2 border-t border-emerald-500/20">
            <div>
              <span className="text-slate-400 block text-[10px]">Workflow</span>
              <span className="font-bold text-slate-100">Vendor Invoice Entry</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px]">Department</span>
              <span className="font-bold text-slate-100">Finance & Ops</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px]">Automation Score</span>
              <span className="font-bold text-emerald-300 font-mono">97%</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px]">Estimated Savings</span>
              <span className="font-bold text-cyan-300 font-mono">2.4 Hours / Day</span>
            </div>
          </div>

          <div className="pt-2 border-t border-emerald-500/20">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Generated Artifacts</span>
            <div className="flex flex-wrap gap-1 text-[9px] font-mono text-slate-300">
              <span className="rounded bg-slate-800 px-1.5 py-0.5 border border-slate-700">Workflow DNA</span>
              <span className="rounded bg-slate-800 px-1.5 py-0.5 border border-slate-700">Playwright Automation</span>
              <span className="rounded bg-slate-800 px-1.5 py-0.5 border border-slate-700">Business Report</span>
              <span className="rounded bg-slate-800 px-1.5 py-0.5 border border-slate-700">Replay</span>
              <span className="rounded bg-slate-800 px-1.5 py-0.5 border border-slate-700">Deployment Package</span>
            </div>
          </div>
        </div>
      ) : (
        /* Component 1 — Live Operations Dashboard Card */
        <div className="flex flex-col gap-3 rounded-xl border border-cyan-500/40 bg-gradient-to-r from-cyan-950/70 to-slate-950 p-4 shadow-xl">
          <div className="flex items-center justify-between border-b border-cyan-500/20 pb-2">
            <div className="flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full bg-emerald-400 animate-pulse" />
              <h4 className="text-xs font-bold text-emerald-300">🟢 Digital Employee Running</h4>
            </div>
            <span className="text-[10px] font-mono text-cyan-400 font-bold bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
              Invoice {activeRecord} / {totalRecords}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-[11px]">
            <div>
              <span className="text-slate-400 block text-[10px]">Status</span>
              <span className="font-bold text-cyan-300 font-mono">Executing</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px]">Runtime</span>
              <span className="font-bold text-purple-300 font-mono">12.4 sec</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px]">Accuracy</span>
              <span className="font-bold text-emerald-300 font-mono">99.4%</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px]">AI Calls / Self-Heals</span>
              <span className="font-bold text-slate-200 font-mono">3 / 1</span>
            </div>
          </div>
        </div>
      )}

      {/* Component 4 — Self-Healing Visibility Card */}
      <div className="rounded-xl border border-amber-500/30 bg-amber-950/20 p-3 text-xs">
        <div className="flex items-center justify-between mb-1.5">
          <div className="flex items-center gap-1.5">
            <RefreshCw className="h-3.5 w-3.5 text-amber-400 animate-spin-slow" />
            <span className="font-bold text-amber-200">Self-Healing Diagnostics</span>
          </div>
          <span className="rounded bg-amber-500/20 px-1.5 py-0.5 text-[9px] font-mono text-amber-300 font-bold border border-amber-500/30">
            Self-Heal Count: 1
          </span>
        </div>
        <p className="text-[10px] text-slate-300 font-mono">
          Execution Failed ──&gt; Gemini Diagnosis ──&gt; Root Cause: Selector Drift ──&gt; Patch v2 Applied ──&gt; Success ✓
        </p>
      </div>

      {/* Component 5 — Enterprise Runtime Metrics Grid */}
      <div className="flex flex-col gap-1.5">
        <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-400">Enterprise Runtime Metrics</span>
        <div className="grid grid-cols-2 gap-2 text-[10px] font-mono">
          <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-2">
            <span className="text-slate-500 block">Execution Time</span>
            <span className="font-bold text-cyan-300">16 sec</span>
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-2">
            <span className="text-slate-500 block">Accuracy</span>
            <span className="font-bold text-emerald-300">99.4%</span>
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-2">
            <span className="text-slate-500 block">Records Completed</span>
            <span className="font-bold text-slate-200">{activeRecord} / 8</span>
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-2">
            <span className="text-slate-500 block">Failures / Recovered</span>
            <span className="font-bold text-emerald-400">0 / 1</span>
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-2">
            <span className="text-slate-500 block">LLM Calls</span>
            <span className="font-bold text-purple-300">3 Calls</span>
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-2">
            <span className="text-slate-500 block">Playwright Actions</span>
            <span className="font-bold text-slate-200">64 Actions</span>
          </div>
        </div>
      </div>

      {/* Component 3 & 2 — AI Decision Stream & Live Execution Timeline */}
      <div className="flex flex-col gap-2">
        <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-400">AI Decision & Execution Stream</span>
        <div className="flex flex-col gap-2 max-h-64 overflow-y-auto pr-1">
          {logs.map((log) => {
            let Icon = CheckCircle2;
            let iconColor = "text-emerald-400";
            let badgeBg = "bg-emerald-500/10 border-emerald-500/20";

            if (log.status === "WARNING") {
              Icon = AlertTriangle;
              iconColor = "text-amber-400";
              badgeBg = "bg-amber-500/10 border-amber-500/20";
            } else if (log.status === "BRANCH") {
              Icon = GitBranch;
              iconColor = "text-purple-400";
              badgeBg = "bg-purple-500/10 border-purple-500/20";
            } else if (log.status === "SPARKLE") {
              Icon = Sparkles;
              iconColor = "text-cyan-400";
              badgeBg = "bg-cyan-500/10 border-cyan-500/20";
            } else if (log.status === "GEMINI") {
              Icon = Zap;
              iconColor = "text-purple-400";
              badgeBg = "bg-purple-500/20 border-purple-500/40";
            } else if (log.status === "SELF_HEAL") {
              Icon = RefreshCw;
              iconColor = "text-amber-400";
              badgeBg = "bg-amber-500/20 border-amber-500/40";
            } else if (log.status === "REPLAY") {
              Icon = Play;
              iconColor = "text-cyan-400";
              badgeBg = "bg-cyan-500/10 border-cyan-500/30";
            }

            return (
              <div
                key={log.id}
                className={`flex items-start justify-between gap-2.5 rounded-xl border p-2.5 transition ${badgeBg}`}
              >
                <div className="flex items-start gap-2.5">
                  <Icon className={`h-4 w-4 shrink-0 mt-0.5 ${iconColor}`} />
                  <div>
                    <div className="flex items-center gap-1.5">
                      <span className="text-[10px] font-mono text-slate-400">{log.timestamp}</span>
                      <h4 className="text-xs font-bold text-slate-100">{log.message}</h4>
                    </div>
                    {log.meta && <p className="text-[10px] text-slate-400 mt-0.5 font-mono">{log.meta}</p>}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Component 7 — Continuous Learning & Drift Monitoring (Future Ready) */}
      <div className="rounded-xl border border-cyan-500/30 bg-slate-950/80 p-3.5 text-xs flex flex-col gap-2">
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-cyan-400 shrink-0 animate-pulse" />
          <span className="font-bold text-cyan-200">Continuous Learning & Drift Monitoring Active</span>
        </div>
        <p className="text-[10px] text-slate-400">
          GhostTrace continuously monitors for process drift. If schema or workflow changes are detected, GhostTrace alerts for approval to auto-update Workflow DNA to v2.
        </p>
        <div className="flex items-center gap-1 text-[9px] font-mono text-cyan-300 pt-1 border-t border-slate-800">
          <span>Continue Monitoring ──&gt; Detect Drift ──&gt; Ask Approval ──&gt; Redeploy v2</span>
        </div>
      </div>
    </div>
  );
};

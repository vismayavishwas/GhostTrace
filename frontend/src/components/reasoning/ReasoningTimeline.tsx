"use client";

import React, { useState, useEffect } from "react";
import { Brain, CheckCircle2, AlertTriangle, GitBranch, Sparkles, WifiOff, Play, Zap } from "lucide-react";
import { WebSocketStreamManager } from "@/lib/websocket";

export interface ReasoningLog {
  id: string;
  timestamp: string;
  message: string;
  status: "CHECK" | "WARNING" | "BRANCH" | "SPARKLE" | "REPLAY" | "GEMINI";
  meta?: string;
}

const INITIAL_EVENT_DRIVEN_LOGS: ReasoningLog[] = [
  { id: "log-1", timestamp: "09:42:11", message: "Pattern Candidate Updated", status: "SPARKLE", meta: "Confidence 97%" },
  { id: "log-2", timestamp: "09:42:12", message: "Gemini 3.1 Flash Lite Called", status: "GEMINI", meta: "Intent Classification (1.42s)" },
  { id: "log-3", timestamp: "09:42:14", message: "Workflow DNA Generated", status: "CHECK", meta: "8 Semantic Steps" },
  { id: "log-4", timestamp: "09:42:15", message: "Business Process Created", status: "BRANCH", meta: "Vendor Invoice Entry" },
  { id: "log-5", timestamp: "09:42:16", message: "Ghost Replay Simulation Started", status: "REPLAY", meta: "Approved DNA Renderer" },
  { id: "log-6", timestamp: "09:42:18", message: "Playwright Compilation Ready", status: "CHECK", meta: "100% Validated" },
];

export const ReasoningTimeline: React.FC = () => {
  const [logs, setLogs] = useState<ReasoningLog[]>(INITIAL_EVENT_DRIVEN_LOGS);
  const [isConnected, setIsConnected] = useState<boolean>(true);

  useEffect(() => {
    // Listen for live replay step synchronization events from GhostReplay
    const handleReplaySync = (e: any) => {
      if (e.detail && e.detail.activeStep) {
        const { stepIndex, activeStep, totalSteps, isComplete } = e.detail;
        const timeStr = new Date().toLocaleTimeString();

        if (isComplete) {
          const completeLog: ReasoningLog = {
            id: `replay-complete-${Date.now()}`,
            timestamp: timeStr,
            message: "Compilation Ready",
            status: "CHECK",
            meta: `All ${totalSteps} DNA steps validated`,
          };
          setLogs((prev) => [completeLog, ...prev.slice(0, 24)]);
        } else {
          const stepLog: ReasoningLog = {
            id: `replay-step-${stepIndex}-${Date.now()}`,
            timestamp: timeStr,
            message: `Replaying step ${stepIndex}/${totalSteps}: ${activeStep.title}`,
            status: "REPLAY",
            meta: `Target: ${activeStep.selector}`,
          };
          setLogs((prev) => {
            if (prev.length > 0 && prev[0].message.startsWith(`Replaying step ${stepIndex}`)) {
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
  }, []);

  return (
    <div className="flex flex-col gap-4 rounded-2xl border border-slate-800/80 bg-slate-900/80 p-5 shadow-xl backdrop-blur-xl h-full">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <div className="flex items-center gap-2">
          <div className="rounded-lg bg-cyan-500/10 p-2 text-cyan-400 border border-cyan-500/20">
            <Brain className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100">AI Reasoning Timeline</h3>
            <p className="text-[10px] text-slate-400">Event-driven decision & pattern analysis trace</p>
          </div>
        </div>

        {isConnected ? (
          <span className="text-[10px] font-mono text-emerald-400 font-bold">● Event Stream Live</span>
        ) : (
          <span className="inline-flex items-center gap-1 text-[10px] font-mono text-amber-400">
            <WifiOff className="h-3 w-3" />
            Waiting for backend...
          </span>
        )}
      </div>

      <div className="flex flex-col gap-2.5 max-h-[460px] overflow-y-auto pr-1">
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
                    <span className="text-[10px] font-mono font-bold text-slate-400">{log.timestamp}</span>
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
  );
};

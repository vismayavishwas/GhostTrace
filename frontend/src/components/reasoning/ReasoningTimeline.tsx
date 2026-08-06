"use client";

import React, { useState, useEffect } from "react";
import { Brain, CheckCircle2, AlertTriangle, GitBranch, Sparkles, WifiOff, Play } from "lucide-react";
import { WebSocketStreamManager } from "@/lib/websocket";

export interface ReasoningLog {
  id: string;
  timestamp: string;
  message: string;
  status: "CHECK" | "WARNING" | "BRANCH" | "SPARKLE" | "REPLAY";
}

export const ReasoningTimeline: React.FC = () => {
  const [logs, setLogs] = useState<ReasoningLog[]>([]);
  const [isConnected, setIsConnected] = useState<boolean>(false);

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
            message: `✓ Replay Complete: Approved Workflow DNA validated across ${totalSteps} steps.`,
            status: "CHECK",
          };
          setLogs((prev) => [completeLog, ...prev.slice(0, 24)]);
        } else {
          const stepLog: ReasoningLog = {
            id: `replay-step-${stepIndex}-${Date.now()}`,
            timestamp: timeStr,
            message: `Replaying approved workflow... Step ${stepIndex}/${totalSteps}: ${activeStep.title} ✓`,
            status: "REPLAY",
          };
          setLogs((prev) => {
            if (prev.length > 0 && prev[0].message.startsWith(`Replaying approved workflow... Step ${stepIndex}`)) {
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
            <p className="text-[10px] text-slate-400">Live decision & pattern analysis trace</p>
          </div>
        </div>

        {isConnected ? (
          <span className="text-[10px] font-mono text-emerald-400 font-bold">● Live Sync</span>
        ) : (
          <span className="inline-flex items-center gap-1 text-[10px] font-mono text-amber-400">
            <WifiOff className="h-3 w-3" />
            Waiting for backend...
          </span>
        )}
      </div>

      <div className="flex flex-col gap-2.5 max-h-[460px] overflow-y-auto pr-1">
        {logs.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-800 p-8 text-center text-xs text-slate-500">
            <span>No AI reasoning logs emitted yet.</span>
            <span className="text-[10px] text-slate-600 mt-1">Waiting for live reasoning stream...</span>
          </div>
        ) : (
          logs.map((log) => {
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
            } else if (log.status === "REPLAY") {
              Icon = Play;
              iconColor = "text-cyan-400";
              badgeBg = "bg-cyan-500/10 border-cyan-500/30";
            }

            return (
              <div
                key={log.id}
                className={`flex items-start gap-2.5 rounded-xl border p-2.5 transition ${badgeBg}`}
              >
                <Icon className={`h-4 w-4 shrink-0 mt-0.5 ${iconColor}`} />
                <div className="flex-1">
                  <p className="text-xs font-semibold text-slate-200">{log.message}</p>
                  <span className="text-[9px] font-mono text-slate-400 block mt-0.5">{log.timestamp}</span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

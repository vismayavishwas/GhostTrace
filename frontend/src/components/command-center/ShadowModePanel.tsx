"use client";

import React, { useState, useEffect } from "react";
import { Eye, CheckCircle2, Zap, WifiOff, Loader2, RotateCcw } from "lucide-react";
import { WebSocketStreamManager } from "@/lib/websocket";
import { fetchTelemetryEvents, resetTelemetryState } from "@/lib/api";

export interface SemanticAction {
  id: string;
  title: string;
  app: string;
  timestamp: string;
  completed: boolean;
}

export interface ShadowModePanelProps {
  repetitionCount?: number;
  maxRepetitions?: number;
  confidenceScore?: number;
  onReset?: () => void;
}

export const ShadowModePanel: React.FC<ShadowModePanelProps> = ({
  repetitionCount = 0,
  maxRepetitions = 5,
  confidenceScore = 0.0,
  onReset,
}) => {
  const [actions, setActions] = useState<SemanticAction[]>([]);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isResetting, setIsResetting] = useState<boolean>(false);

  const handleReset = async () => {
    setIsResetting(true);
    await resetTelemetryState();
    setActions([]);
    if (onReset) onReset();
    setIsResetting(false);
  };

  useEffect(() => {
    const syncTelemetry = () => {
      fetchTelemetryEvents()
        .then((data) => {
          if (Array.isArray(data)) {
            const mapped = data.map((item: any, idx: number) => ({
              id: item.event_id || `evt-${idx}`,
              title: `${item.event_type} on ${item.target_selector || item.element_tag || 'element'}`,
              app: item.app_title || item.active_tab || "Web App",
              timestamp: item.timestamp ? new Date(item.timestamp).toLocaleTimeString() : "Just now",
              completed: true,
            }));
            setActions(mapped);
          }
          setIsLoading(false);
        })
        .catch(() => setIsLoading(false));
    };

    syncTelemetry();
    const interval = setInterval(syncTelemetry, 1000);

    // Connect to live WebSocket stream
    const wsManager = new WebSocketStreamManager(
      "telemetry",
      (msg) => {
        if (msg && msg.payload) {
          syncTelemetry();
        }
      },
      (connected) => setIsConnected(connected)
    );

    return () => {
      clearInterval(interval);
      wsManager.close();
    };
  }, []);


  const confidencePct = Math.round(confidenceScore * 100);

  return (
    <div className="flex flex-col gap-4 rounded-2xl border border-slate-800/80 bg-slate-900/80 p-5 shadow-xl backdrop-blur-xl h-full">
      {/* Panel Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <div className="flex items-center gap-2">
          <div className="rounded-lg bg-cyan-500/10 p-2 text-cyan-400 border border-cyan-500/20">
            <Eye className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100">Shadow Mode Perception</h3>
            <p className="text-[10px] text-slate-400">Passive background action observation</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleReset}
            disabled={isResetting}
            title="Clear all observed actions & reset shadow mode to 0"
            className="flex items-center gap-1.5 rounded-lg border border-slate-700/60 bg-slate-800/60 px-2.5 py-1 text-xs font-semibold text-slate-300 hover:bg-slate-700 hover:text-white transition disabled:opacity-50"
          >
            <RotateCcw className={`h-3.5 w-3.5 ${isResetting ? "animate-spin text-cyan-400" : "text-slate-400"}`} />
            <span>{isResetting ? "Resetting..." : "Restart Shadow Mode"}</span>
          </button>

          {isConnected ? (
            <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-[10px] font-bold text-emerald-400 border border-emerald-500/20">
              ● Live Stream
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 rounded-full bg-amber-500/10 px-2.5 py-0.5 text-[10px] font-bold text-amber-400 border border-amber-500/20">
              <WifiOff className="h-3 w-3" />
              Waiting for backend...
            </span>
          )}
        </div>
      </div>


      {/* Repetition & Confidence Metrics */}
      <div className="grid grid-cols-2 gap-3 rounded-xl border border-slate-800/60 bg-slate-950/50 p-3">
        <div>
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Pattern Repetition</span>
          <div className="mt-1 flex items-baseline gap-1">
            <span className="text-lg font-black font-mono text-cyan-400">{repetitionCount}</span>
            <span className="text-xs text-slate-500">/ {maxRepetitions} runs</span>
          </div>
        </div>

        <div>
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Learning Confidence</span>
          <div className="mt-1 flex items-baseline gap-1">
            <span className="text-lg font-black font-mono text-purple-400">{confidencePct}%</span>
            <Zap className="h-3 w-3 text-purple-400 inline" />
          </div>
        </div>
      </div>

      {/* Clean High-Level User Actions Stream */}
      <div className="flex flex-col gap-2 flex-1">
        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Observed User Actions</span>
        
        {isLoading ? (
          <div className="flex items-center justify-center py-8 text-xs text-slate-500 gap-2">
            <Loader2 className="h-4 w-4 animate-spin text-cyan-400" />
            <span>Fetching backend telemetry...</span>
          </div>
        ) : actions.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-800 p-6 text-center text-xs text-slate-500">
            <span>No telemetry events recorded yet.</span>
            <span className="text-[10px] text-slate-600 mt-1">Waiting for backend telemetry stream...</span>
          </div>
        ) : (
          <div className="flex flex-col gap-2 max-h-80 overflow-y-auto pr-1">
            {actions.map((act) => (
              <div
                key={act.id}
                className="flex items-center justify-between rounded-lg border border-slate-800/60 bg-slate-950/40 p-2.5 transition hover:border-slate-700/80"
              >
                <div className="flex items-center gap-2.5">
                  <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
                  <div>
                    <h4 className="text-xs font-semibold text-slate-200">{act.title}</h4>
                    <span className="text-[10px] text-slate-500 font-mono">{act.app}</span>
                  </div>
                </div>
                <span className="text-[10px] font-mono text-slate-500">{act.timestamp}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

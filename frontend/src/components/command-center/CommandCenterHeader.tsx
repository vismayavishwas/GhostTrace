"use client";

import React from "react";
import { Ghost, Eye, Activity, ShieldCheck } from "lucide-react";

export interface CommandCenterHeaderProps {
  shadowModeActive?: boolean;
  monitoredApps?: string[];
  confidenceScore?: number; // 0.35 to 0.97
}

export const CommandCenterHeader: React.FC<CommandCenterHeaderProps> = ({
  shadowModeActive = true,
  monitoredApps = ["Chrome", "SAP ERP", "Excel"],
  confidenceScore = 0.97,
}) => {
  const confidencePct = Math.round(confidenceScore * 100);

  return (
    <header className="flex flex-col md:flex-row items-center justify-between gap-4 rounded-2xl border border-slate-800/80 bg-slate-900/90 px-6 py-4 shadow-2xl backdrop-blur-xl">
      {/* Left Title & Status */}
      <div className="flex items-center gap-4">
        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-500/20 to-purple-500/20 text-cyan-400 border border-cyan-500/30 shadow-lg shadow-cyan-500/10">
          <Ghost className="h-6 w-6 animate-pulse" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-black tracking-tight text-white font-mono">GhostTrace AI OS</h1>
            <span className="inline-flex items-center gap-1 rounded-md bg-cyan-500/10 px-2 py-0.5 text-[10px] font-bold text-cyan-400 border border-cyan-500/20">
              v2.5 Enterprise
            </span>
          </div>
          <p className="text-[11px] text-slate-400">Autonomous Perception & Execution Operating System</p>
        </div>
      </div>

      {/* Center Status Badges */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 rounded-full border border-slate-800 bg-slate-950/60 px-3.5 py-1.5 text-xs">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-500"></span>
          </span>
          <span className="font-semibold text-slate-200">Shadow Mode</span>
          <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider">Active</span>
        </div>

        <div className="hidden sm:flex items-center gap-1.5 rounded-full border border-slate-800 bg-slate-950/60 px-3 py-1.5 text-xs text-slate-400">
          <Eye className="h-3.5 w-3.5 text-purple-400" />
          <span>Apps:</span>
          {monitoredApps.map((app, idx) => (
            <span key={idx} className="rounded bg-slate-800 px-1.5 py-0.5 text-[10px] font-semibold text-slate-300">
              {app}
            </span>
          ))}
        </div>
      </div>

      {/* Right Live Confidence Meter */}
      <div className="flex items-center gap-4">
        <div className="flex flex-col items-end">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">Global Pattern Confidence</span>
          <div className="flex items-center gap-2">
            <div className="h-2 w-24 rounded-full bg-slate-800 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-cyan-500 to-purple-500 transition-all duration-500"
                style={{ width: `${confidencePct}%` }}
              />
            </div>
            <span className="text-sm font-bold font-mono text-cyan-400">{confidencePct}%</span>
          </div>
        </div>

        <div className="hidden lg:flex items-center gap-1.5 rounded-lg bg-emerald-500/10 px-2.5 py-1.5 text-xs font-bold text-emerald-400 border border-emerald-500/20">
          <ShieldCheck className="h-4 w-4" />
          <span>99.9% Isolated</span>
        </div>
      </div>
    </header>
  );
};

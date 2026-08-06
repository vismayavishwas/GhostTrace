import React from "react";
import { Activity, ShieldCheck, Cpu } from "lucide-react";

export const Header: React.FC = () => {
  return (
    <header className="w-full glass-panel border-b border-surface-border px-6 py-3.5 flex items-center justify-between z-50">
      <div className="flex items-center space-x-3">
        <div className="h-9 w-9 rounded-lg bg-gradient-to-tr from-indigo-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
          <Cpu className="h-5 w-5 text-white" />
        </div>
        <div>
          <h1 className="text-lg font-bold text-slate-100 tracking-tight flex items-center gap-2">
            GhostTrace <span className="text-xs px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">AI</span>
          </h1>
          <p className="text-xs text-slate-400">Autonomous Process Intelligence Platform</p>
        </div>
      </div>

      <div className="flex items-center space-x-6">
        <div className="flex items-center space-x-2 text-xs">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="text-slate-300 font-medium">Orchestrator: IDLE</span>
        </div>

        <div className="h-4 w-[1px] bg-slate-800" />

        <div className="flex items-center space-x-2 text-xs text-slate-400 bg-slate-900/60 px-3 py-1.5 rounded-full border border-slate-800">
          <ShieldCheck className="h-3.5 w-3.5 text-indigo-400" />
          <span>Vertex AI Gemini 3.0</span>
        </div>
      </div>
    </header>
  );
};

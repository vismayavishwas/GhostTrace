"use client";

import React from "react";
import { Sparkles, ArrowRight, Zap } from "lucide-react";

export interface WorkflowCandidatePanelProps {
  confidenceScore?: number;
  candidateName?: string;
  onAnalyzeTrigger: () => void;
}

export const WorkflowCandidatePanel: React.FC<WorkflowCandidatePanelProps> = ({
  confidenceScore = 0.0,
  candidateName = "Product Copy-Paste Entry Workflow",
  onAnalyzeTrigger,
}) => {
  const confidencePct = Math.round(confidenceScore * 100);

  return (
    <div className="flex flex-col md:flex-row items-center justify-between gap-4 rounded-2xl border border-cyan-500/40 bg-gradient-to-r from-cyan-950/80 via-slate-900/90 to-purple-950/80 p-5 shadow-2xl backdrop-blur-xl">
      <div className="flex items-center gap-3.5">
        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 shadow-lg shadow-cyan-500/10">
          <Sparkles className="h-6 w-6 animate-spin" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-black text-white">Workflow Candidate Discovered</h3>
            <span className="rounded-full bg-cyan-500/20 px-2.5 py-0.5 text-[10px] font-extrabold text-cyan-300 border border-cyan-500/30">
              {confidencePct > 0 ? `${confidencePct}% Confidence` : "Pattern Detected"}
            </span>
          </div>
          <p className="text-xs text-slate-300">Target: {candidateName}</p>
        </div>
      </div>

      <button
        onClick={onAnalyzeTrigger}
        className="flex items-center gap-2 rounded-xl bg-cyan-500 px-6 py-3 text-xs font-black text-slate-950 shadow-xl shadow-cyan-500/30 hover:bg-cyan-400 hover:shadow-cyan-500/50 transition-all duration-200 transform hover:-translate-y-0.5"
      >
        <Zap className="h-4 w-4" />
        <span>Analyze & Build Automation</span>
        <ArrowRight className="h-4 w-4" />
      </button>
    </div>
  );
};

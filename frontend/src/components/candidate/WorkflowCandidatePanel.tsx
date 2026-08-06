"use client";

import React from "react";
import { Sparkles, ArrowRight, Zap } from "lucide-react";

export interface BusinessProcessData {
  workflow_name?: string;
  department?: string;
  business_goal?: string;
  confidence?: number;
  repeatability?: string;
  automation_readiness?: string;
  summary?: string;
}

export interface WorkflowCandidatePanelProps {
  confidenceScore?: number;
  candidateName?: string;
  businessProcess?: BusinessProcessData | null;
  onAnalyzeTrigger: () => void;
}

export const WorkflowCandidatePanel: React.FC<WorkflowCandidatePanelProps> = ({
  confidenceScore = 0.0,
  candidateName = "Enterprise Data Transfer Workflow",
  businessProcess,
  onAnalyzeTrigger,
}) => {
  const confidencePct = Math.round(confidenceScore * 100);

  const title = businessProcess?.workflow_name || candidateName;
  const dept = businessProcess?.department || "Operations & IT";
  const readiness = businessProcess?.automation_readiness || "High Readiness";
  const obsCount = businessProcess?.repeatability || "3 Observations";
  const summaryText = businessProcess?.summary || "Automates repetitive cross-app data entry workflow.";

  return (
    <div className="flex flex-col md:flex-row items-center justify-between gap-4 rounded-2xl border border-cyan-500/40 bg-gradient-to-r from-cyan-950/80 via-slate-900/90 to-purple-950/80 p-5 shadow-2xl backdrop-blur-xl">
      <div className="flex items-center gap-3.5">
        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 shadow-lg shadow-cyan-500/10 shrink-0">
          <Sparkles className="h-6 w-6 animate-spin" />
        </div>
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="text-sm font-black text-white">{title}</h3>
            <span className="rounded-full bg-cyan-500/20 px-2.5 py-0.5 text-[10px] font-extrabold text-cyan-300 border border-cyan-500/30">
              {confidencePct > 0 ? `${confidencePct}% Confidence` : "Pattern Detected"}
            </span>
            <span className="rounded-full bg-purple-500/20 px-2.5 py-0.5 text-[10px] font-extrabold text-purple-300 border border-purple-500/30">
              🏢 {dept}
            </span>
            <span className="rounded-full bg-emerald-500/20 px-2.5 py-0.5 text-[10px] font-extrabold text-emerald-300 border border-emerald-500/30">
              🔁 {obsCount}
            </span>
            <span className="rounded-full bg-amber-500/20 px-2.5 py-0.5 text-[10px] font-extrabold text-amber-300 border border-amber-500/30">
              ⚡ {readiness}
            </span>
          </div>
          <p className="text-xs text-slate-300 mt-1">{summaryText}</p>
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

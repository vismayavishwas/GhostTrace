"use client";

import React from "react";
import { TrendingUp, Clock, MousePointerClick, ShieldCheck } from "lucide-react";

export interface AutomationImpactCardProps {
  hoursSavedPerWeek?: number; // e.g. 4.2
  clicksEliminated?: number; // e.g. 48
  accuracyConfidence?: number; // e.g. 97
}

export const AutomationImpactCard: React.FC<AutomationImpactCardProps> = ({
  hoursSavedPerWeek = 4.2,
  clicksEliminated = 48,
  accuracyConfidence = 97,
}) => {
  return (
    <div className="flex flex-col md:flex-row items-center justify-between gap-4 rounded-2xl border border-slate-800/80 bg-slate-900/90 p-5 shadow-xl backdrop-blur-xl">
      <div className="flex items-center gap-3">
        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-md">
          <TrendingUp className="h-6 w-6" />
        </div>
        <div>
          <h3 className="text-sm font-bold text-slate-100">Automation Impact ROI</h3>
          <p className="text-[11px] text-slate-400">Estimated efficiency gain per worker</p>
        </div>
      </div>

      <div className="flex items-center gap-6 text-xs">
        <div className="flex items-center gap-2">
          <Clock className="h-4 w-4 text-cyan-400" />
          <div>
            <span className="text-[10px] text-slate-400 block">Time Saved</span>
            <span className="font-bold font-mono text-slate-100">{hoursSavedPerWeek} hrs/wk</span>
          </div>
        </div>

        <div className="h-6 w-[1px] bg-slate-800" />

        <div className="flex items-center gap-2">
          <MousePointerClick className="h-4 w-4 text-purple-400" />
          <div>
            <span className="text-[10px] text-slate-400 block">Clicks Saved</span>
            <span className="font-bold font-mono text-slate-100">{clicksEliminated} clicks/run</span>
          </div>
        </div>

        <div className="h-6 w-[1px] bg-slate-800" />

        <div className="flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-emerald-400" />
          <div>
            <span className="text-[10px] text-slate-400 block">Accuracy</span>
            <span className="font-bold font-mono text-emerald-400">{accuracyConfidence}% Verified</span>
          </div>
        </div>
      </div>
    </div>
  );
};

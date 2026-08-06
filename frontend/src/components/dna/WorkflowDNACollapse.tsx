"use client";

import React, { useState } from "react";
import { Dna, ArrowRight, Layers, CheckCircle2 } from "lucide-react";

export interface WorkflowDNACollapseProps {
  onProceed?: () => void;
}

export const WorkflowDNACollapse: React.FC<WorkflowDNACollapseProps> = ({ onProceed }) => {
  const [collapsed, setCollapsed] = useState<boolean>(true);

  const semanticSteps = [
    { title: "Portal Authentication & Navigation", rawCount: 8, app: "Chrome" },
    { title: "Extract Vendor Invoice Metadata", rawCount: 11, app: "PDF Reader" },
    { title: "Post Invoice Entry to SAP ERP", rawCount: 5, app: "SAP Portal" },
  ];

  return (
    <div className="flex flex-col gap-6 rounded-2xl border border-slate-800/80 bg-slate-900/90 p-6 shadow-2xl backdrop-blur-xl">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
        <div>
          <span className="inline-flex items-center gap-1.5 rounded-md bg-purple-500/10 px-2.5 py-1 text-xs font-bold text-purple-400 border border-purple-500/20">
            🧬 Semantic DNA Compression
          </span>
          <h2 className="mt-2 text-lg font-bold text-white">Workflow DNA Extraction</h2>
          <p className="text-xs text-slate-400">Collapsing raw clicks & keystrokes into intent-driven business steps.</p>
        </div>

        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex items-center gap-1.5 rounded-xl border border-purple-500/30 bg-purple-500/10 px-3.5 py-2 text-xs font-bold text-purple-400 hover:bg-purple-500/20 transition"
        >
          <Layers className="h-4 w-4" />
          <span>{collapsed ? "Expand 24 Raw Events" : "Collapse into 3 Business Steps"}</span>
        </button>
      </div>

      {/* Collapse Container */}
      <div className="flex flex-col gap-3">
        {semanticSteps.map((step, idx) => (
          <div
            key={idx}
            className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/60 p-4 shadow-md backdrop-blur-sm transition-all duration-300 hover:border-purple-500/40"
          >
            <div className="flex items-center gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-purple-500/10 text-purple-400 font-bold font-mono text-sm border border-purple-500/20">
                0{idx + 1}
              </div>
              <div>
                <h4 className="text-xs font-bold text-slate-100">{step.title}</h4>
                <p className="text-[10px] text-slate-400">Target: {step.app}</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <span className="rounded-full bg-slate-800 px-2.5 py-1 text-[10px] font-mono text-cyan-400 border border-slate-700">
                {step.rawCount} raw clicks collapsed
              </span>
              <CheckCircle2 className="h-4 w-4 text-emerald-400" />
            </div>
          </div>
        ))}
      </div>

      {onProceed && (
        <div className="flex justify-end pt-2">
          <button
            onClick={onProceed}
            className="flex items-center gap-2 rounded-xl bg-purple-500 px-5 py-2.5 text-xs font-bold text-slate-950 shadow-lg shadow-purple-500/25 hover:bg-purple-400 transition-all"
          >
            <span>Generate Automation Blueprint</span>
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      )}
    </div>
  );
};

"use client";

import React, { useState } from "react";
import { Dna, ArrowRight, Layers, CheckCircle2, FileText, ArrowRightLeft } from "lucide-react";

export interface WorkflowDNACollapseProps {
  workflowDNA?: any;
  onProceed?: () => void;
}

export const WorkflowDNACollapse: React.FC<WorkflowDNACollapseProps> = ({ workflowDNA, onProceed }) => {
  const [showRawDetail, setShowRawDetail] = useState<boolean>(false);

  const title = workflowDNA?.name || "Cross-Application Workflow Automation";
  const description =
    workflowDNA?.description ||
    "Dynamic semantic workflow mapping human-understood field flows and intent-driven business steps.";

  const rawMappings = workflowDNA?.metadata?.field_mappings || workflowDNA?.field_mappings || [];
  const activeMappings = rawMappings;
  const sourceAppTitle = activeMappings[0]?.source_app || "Source Application";

  const rawSteps = workflowDNA?.steps || [];
  const activeSteps = rawSteps;

  return (
    <div className="flex flex-col gap-6 rounded-2xl border border-slate-800/80 bg-slate-900/90 p-6 shadow-2xl backdrop-blur-xl">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div>
          <span className="inline-flex items-center gap-1.5 rounded-md bg-purple-500/10 px-2.5 py-1 text-xs font-bold text-purple-400 border border-purple-500/20">
            🧬 Workflow DNA
          </span>
          <h2 className="mt-2 text-lg font-bold text-white">{title}</h2>
          <p className="text-xs text-slate-400">{description}</p>
        </div>

        <button
          onClick={() => setShowRawDetail(!showRawDetail)}
          className="flex items-center gap-1.5 rounded-xl border border-purple-500/30 bg-purple-500/10 px-3.5 py-2 text-xs font-bold text-purple-400 hover:bg-purple-500/20 transition"
        >
          <Layers className="h-4 w-4" />
          <span>{showRawDetail ? "Hide Mapping Metadata" : "View Field Lineage"}</span>
        </button>
      </div>

      {/* Human-Understood Visual Field Flowchart Abstraction */}
      <div className="flex flex-col gap-3 rounded-xl border border-cyan-500/30 bg-slate-950/80 p-5 shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
          <div className="flex items-center gap-2">
            <FileText className="h-4.5 w-4.5 text-cyan-400" />
            <span className="font-bold text-xs text-cyan-300 font-mono tracking-wide">
              📄 Discovered Field Lineage Flowchart
            </span>
          </div>
          <span className="text-[10px] font-mono text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
            {sourceAppTitle}
          </span>
        </div>

        {activeMappings.length > 0 ? (
          <div className="flex flex-col gap-3 py-2">
            {activeMappings.map((m: any, idx: number) => (
              <div key={idx} className="flex items-center gap-3 text-xs font-mono flex-wrap bg-slate-900/40 p-3 rounded-xl border border-slate-800/80">
                <span className="text-cyan-400 font-bold">Step {idx + 1}</span>
                <span className="font-bold text-slate-100 bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-700 shadow-sm">
                  {m.source_label || "Source Field"}
                </span>
                <span className="text-cyan-400 font-bold tracking-tighter text-sm">─────────▶</span>
                <span className="font-bold text-emerald-300 bg-emerald-950/60 px-3 py-1.5 rounded-lg border border-emerald-500/40 shadow-sm">
                  {m.destination_label || "Target Field"}
                </span>
                {m.destination_app && (
                  <span className="text-[10px] text-slate-400 font-sans ml-auto bg-slate-950 px-2 py-1 rounded border border-slate-800">
                    Target: {m.destination_app}
                  </span>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="p-4 text-xs text-slate-400 font-mono italic">
            Waiting for cross-application telemetry transfers... Interact with fields in the sandbox to observe dynamic Workflow DNA.
          </div>
        )}
      </div>

      {/* Human-Readable Business Step Sequence */}
      <div className="flex flex-col gap-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">
          Intent-Driven Business Steps
        </h3>
        {activeSteps.map((step: any, idx: number) => (
          <div
            key={idx}
            className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/60 p-4 shadow-md backdrop-blur-sm transition-all duration-300 hover:border-purple-500/40"
          >
            <div className="flex items-center gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-purple-500/10 text-purple-400 font-bold font-mono text-sm border border-purple-500/20 shrink-0">
                0{idx + 1}
              </div>
              <div>
                <h4 className="text-xs font-bold text-slate-100">{step.action_name}</h4>
                <p className="text-[10px] text-slate-400">Target Application: {step.target_app}</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <span className="rounded-full bg-slate-800 px-2.5 py-1 text-[10px] font-mono text-cyan-400 border border-slate-700">
                Human Business Step
              </span>
              <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
            </div>
          </div>
        ))}
      </div>

      {showRawDetail && (
        <div className="rounded-xl border border-slate-800 bg-slate-950/90 p-4 text-[11px] font-mono text-slate-400 animate-in fade-in duration-200">
          <span className="text-cyan-400 font-bold">Internal Deterministic Fingerprints (Hidden from End-User):</span>
          <pre className="mt-2 overflow-x-auto text-[10px] text-slate-500 leading-relaxed">
            {JSON.stringify({ workflow_id: workflowDNA?.workflow_id, mappings: activeMappings }, null, 2)}
          </pre>
        </div>
      )}

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


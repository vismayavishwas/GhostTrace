"use client";

import React, { useState } from "react";
import { Dna, ArrowRight, Layers, CheckCircle2, FileText, ChevronDown, ChevronUp, Database, Sparkles } from "lucide-react";

export interface WorkflowDNACollapseProps {
  workflowDNA?: any;
  onProceed?: () => void;
}

export const WorkflowDNACollapse: React.FC<WorkflowDNACollapseProps> = ({ workflowDNA, onProceed }) => {
  const [showRawDetail, setShowRawDetail] = useState<boolean>(false);
  const [expandedMappingIdx, setExpandedMappingIdx] = useState<number | null>(null);

  const title = workflowDNA?.name || "Dynamic Semantic Workflow";
  const description =
    workflowDNA?.description ||
    "Observed semantic graph reconstructed from live browser telemetry transfers.";

  const rawMappings = workflowDNA?.metadata?.field_mappings || workflowDNA?.field_mappings || [];
  const activeMappings = rawMappings;

  const rawSteps = workflowDNA?.steps || [];
  const activeSteps = rawSteps;

  const toggleMappingExpand = (idx: number) => {
    setExpandedMappingIdx(expandedMappingIdx === idx ? null : idx);
  };

  return (
    <div className="flex flex-col gap-6 rounded-2xl border border-slate-800/80 bg-slate-900/90 p-6 shadow-2xl backdrop-blur-xl">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div>
          <span className="inline-flex items-center gap-1.5 rounded-md bg-purple-500/10 px-2.5 py-1 text-xs font-bold text-purple-400 border border-purple-500/20">
            🧬 Workflow DNA Graph
          </span>
          <h2 className="mt-2 text-lg font-bold text-white">{title}</h2>
          <p className="text-xs text-slate-400">{description}</p>
        </div>

        <button
          onClick={() => setShowRawDetail(!showRawDetail)}
          className="flex items-center gap-1.5 rounded-xl border border-purple-500/30 bg-purple-500/10 px-3.5 py-2 text-xs font-bold text-purple-400 hover:bg-purple-500/20 transition"
        >
          <Layers className="h-4 w-4" />
          <span>{showRawDetail ? "Hide Raw JSON" : "View Graph JSON"}</span>
        </button>
      </div>

      {/* Dynamic Visual Field Flowchart */}
      <div className="flex flex-col gap-3 rounded-xl border border-cyan-500/30 bg-slate-950/80 p-5 shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
          <div className="flex items-center gap-2">
            <FileText className="h-4.5 w-4.5 text-cyan-400" />
            <span className="font-bold text-xs text-cyan-300 font-mono tracking-wide">
              📄 Learned Field Flowchart
            </span>
          </div>
          <span className="text-[10px] font-mono text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
            {activeMappings.length} Learned Mappings
          </span>
        </div>

        {activeMappings.length > 0 ? (
          <div className="flex flex-col gap-3 py-2">
            {activeMappings.map((m: any, idx: number) => {
              const srcApp = m.source_app || "Unknown Application";
              const srcLbl = m.source_label || "Unknown Field";
              const destApp = m.destination_app || "Unknown Application";
              const destLbl = m.destination_label || "Unknown Field";

              return (
                <div key={idx} className="flex flex-col gap-2 bg-slate-900/60 p-3.5 rounded-xl border border-slate-800">
                  <div className="flex items-center justify-between gap-3 text-xs font-mono flex-wrap">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-cyan-400 font-bold">Flow #{idx + 1}</span>

                      {/* Source Node */}
                      <div className="flex items-center gap-1.5 bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800">
                        <span className="text-[10px] text-slate-400">{srcApp}:</span>
                        <span className="font-bold text-slate-100">{srcLbl}</span>
                      </div>

                      <span className="text-cyan-400 font-bold text-sm">─────────▶</span>

                      {/* Destination Node */}
                      <div className="flex items-center gap-1.5 bg-emerald-950/60 px-2.5 py-1 rounded-lg border border-emerald-500/40">
                        <span className="text-[10px] text-emerald-400">{destApp}:</span>
                        <span className="font-bold text-emerald-200">{destLbl}</span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="p-4 text-xs text-slate-400 font-mono italic">
            Waiting for cross-application telemetry transfers... Interact with fields in the sandbox to observe dynamic Workflow DNA.
          </div>
        )}
      </div>

      {/* Expandable Mapping Metadata List Section */}
      {activeMappings.length > 0 && (
        <div className="flex flex-col gap-3 rounded-xl border border-purple-500/30 bg-slate-950/80 p-5 shadow-xl">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
            <div className="flex items-center gap-2">
              <Database className="h-4.5 w-4.5 text-purple-400" />
              <span className="font-bold text-xs text-purple-300 font-mono tracking-wide">
                📋 Field Mapping Metadata & Attributes
              </span>
            </div>
            <span className="text-[10px] font-mono text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
              Click item to inspect attributes
            </span>
          </div>

          <div className="flex flex-col gap-2.5 pt-1">
            {activeMappings.map((m: any, idx: number) => {
              const isExpanded = expandedMappingIdx === idx;
              const srcLbl = m.source_label || "Unknown Field";
              const destLbl = m.destination_label || "Unknown Field";

              return (
                <div
                  key={idx}
                  className={`flex flex-col rounded-xl border transition-all duration-200 overflow-hidden ${
                    isExpanded ? "border-purple-500/50 bg-slate-900/90 shadow-lg" : "border-slate-800 bg-slate-900/40 hover:border-slate-700"
                  }`}
                >
                  {/* Item Header Button */}
                  <button
                    onClick={() => toggleMappingExpand(idx)}
                    className="flex items-center justify-between p-3.5 text-left text-xs font-mono w-full"
                  >
                    <div className="flex items-center gap-2.5">
                      <span className="flex h-5 w-5 items-center justify-center rounded bg-purple-500/20 text-[10px] font-bold text-purple-300 border border-purple-500/30">
                        {idx + 1}
                      </span>
                      <span className="font-bold text-slate-200">
                        {srcLbl} ➔ {destLbl}
                      </span>
                    </div>

                    <div className="flex items-center gap-2 text-slate-400">
                      <span className="text-[10px] bg-slate-950 px-2 py-0.5 rounded border border-slate-800 font-sans">
                        {isExpanded ? "Collapse Metadata" : "View Details"}
                      </span>
                      {isExpanded ? <ChevronUp className="h-4 w-4 text-purple-400" /> : <ChevronDown className="h-4 w-4 text-slate-400" />}
                    </div>
                  </button>

                  {/* Dropdown Content - Only rendered when expanded */}
                  {isExpanded && (
                    <div className="flex flex-col gap-2.5 p-4 border-t border-slate-800/80 bg-slate-950/90 text-xs font-mono text-slate-300 animate-in slide-in-from-top-2 duration-200">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div className="flex flex-col gap-1 bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                          <span className="text-[10px] text-cyan-400 font-bold">SOURCE APPLICATION</span>
                          <span className="text-slate-100 font-semibold">{m.source_app || "Unknown Application"}</span>
                          <span className="text-[10px] text-slate-400 truncate">Entity: {m.source_entity || m.source_label}</span>
                        </div>

                        <div className="flex flex-col gap-1 bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                          <span className="text-[10px] text-emerald-400 font-bold">TARGET APPLICATION</span>
                          <span className="text-slate-100 font-semibold">{m.destination_app || "Unknown Application"}</span>
                          <span className="text-[10px] text-slate-400 truncate">Entity: {m.destination_entity || m.destination_label}</span>
                        </div>
                      </div>

                      {m.pasted_value && (
                        <div className="flex flex-col gap-1 bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                          <span className="text-[10px] text-purple-400 font-bold">SAMPLE PASTED VALUE</span>
                          <span className="text-amber-300 bg-slate-950 px-2 py-1 rounded font-mono text-[11px] border border-slate-800">
                            "{m.pasted_value}"
                          </span>
                        </div>
                      )}

                      <div className="flex items-center justify-between text-[10px] text-slate-500 pt-1 border-t border-slate-900">
                        <span>Transfer ID: {m.transfer_id || "xfer-auto"}</span>
                        <span className="text-emerald-400 font-bold">✓ Direct Transfer Verified</span>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Chronological Step Sequence */}
      <div className="flex flex-col gap-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">
          Chronological Business Actions
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
                <p className="text-[10px] text-slate-400">Application: {step.target_app || "Unknown Application"}</p>
              </div>
            </div>

            <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
          </div>
        ))}
      </div>

      {showRawDetail && (
        <div className="rounded-xl border border-slate-800 bg-slate-950/90 p-4 text-[11px] font-mono text-slate-400 animate-in fade-in duration-200">
          <span className="text-cyan-400 font-bold">Internal Workflow DNA Graph:</span>
          <pre className="mt-2 overflow-x-auto text-[10px] text-slate-500 leading-relaxed">
            {JSON.stringify({ workflow_id: workflowDNA?.workflow_id, mappings: activeMappings, steps: activeSteps }, null, 2)}
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

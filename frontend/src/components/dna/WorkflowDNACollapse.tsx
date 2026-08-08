"use client";

import React, { useState } from "react";
import {
  Dna,
  ArrowRight,
  Layers,
  CheckCircle2,
  FileText,
  ChevronDown,
  ChevronUp,
  Database,
  Sparkles,
  ArrowDownRight,
  ExternalLink,
  Laptop,
  ArrowDown,
  Terminal,
  Activity
} from "lucide-react";

export interface WorkflowDNACollapseProps {
  workflowDNA?: any;
  fieldMappings?: any[];
  chronologicalTransfers?: any[];
  observationSessionId?: string;
  repetitionCount?: number;
  onProceed?: () => void;
}

export const WorkflowDNACollapse: React.FC<WorkflowDNACollapseProps> = ({
  workflowDNA,
  fieldMappings = [],
  chronologicalTransfers = [],
  observationSessionId = "",
  repetitionCount = 0,
  onProceed,
}) => {
  const [showDeveloperDetails, setShowDeveloperDetails] = useState<boolean>(false);
  const [expandedMappingIdx, setExpandedMappingIdx] = useState<number | null>(null);

  const title = workflowDNA?.name || "Discovered Enterprise Workflow";
  const description =
    workflowDNA?.description ||
    "Observed cross-application business process graph reconstructed dynamically from live browser telemetry.";

  // Read chronological sequence transfers directly from props or Workflow DNA metadata
  const activeTransfers = chronologicalTransfers.length > 0
    ? chronologicalTransfers
    : (fieldMappings.length > 0
      ? fieldMappings
      : (workflowDNA?.metadata?.chronological_transfers || workflowDNA?.metadata?.field_mappings || workflowDNA?.field_mappings || []));

  const rawSteps = workflowDNA?.steps || [];
  const activeSteps = rawSteps;

  const toggleMappingExpand = (idx: number) => {
    setExpandedMappingIdx(expandedMappingIdx === idx ? null : idx);
  };

  return (
    <div className="flex flex-col gap-6 rounded-2xl border border-slate-800/80 bg-slate-900/90 p-6 shadow-2xl backdrop-blur-xl">
      {/* Top Header & Overview */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="inline-flex items-center gap-1.5 rounded-md bg-purple-500/10 px-2.5 py-1 text-xs font-bold text-purple-400 border border-purple-500/20">
              🧬 Discovered Business Process Map
            </span>
            {workflowDNA?.confidence_score && (
              <span className="inline-flex items-center gap-1 rounded-md bg-emerald-500/10 px-2.5 py-1 text-xs font-mono font-bold text-emerald-400 border border-emerald-500/20">
                <Sparkles className="h-3 w-3" />
                <span>{Math.round(workflowDNA.confidence_score * 100)}% Semantic Consistency</span>
              </span>
            )}
            {observationSessionId && (
              <span className="inline-flex items-center gap-1 rounded-md bg-cyan-500/10 px-2.5 py-1 text-xs font-mono text-cyan-400 border border-cyan-500/20">
                <span>Session: {observationSessionId}</span>
              </span>
            )}
          </div>
          <h2 className="mt-2.5 text-xl font-extrabold text-white tracking-tight">{title}</h2>
          <p className="mt-1 text-xs text-slate-400 leading-relaxed max-w-3xl">{description}</p>
        </div>

        <button
          onClick={() => setShowDeveloperDetails(!showDeveloperDetails)}
          className="flex items-center gap-1.5 rounded-xl border border-purple-500/30 bg-purple-500/10 px-3.5 py-2 text-xs font-bold text-purple-300 hover:bg-purple-500/20 transition shrink-0"
        >
          <Terminal className="h-4 w-4 text-purple-400" />
          <span>{showDeveloperDetails ? "Hide Developer Info" : "Developer & Fingerprints"}</span>
        </button>
      </div>

      {/* Dynamic Process Discovery Diagram */}
      <div className="flex flex-col gap-4 rounded-xl border border-cyan-500/30 bg-slate-950/90 p-5 shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
          <div className="flex items-center gap-2">
            <Activity className="h-4.5 w-4.5 text-cyan-400" />
            <span className="font-bold text-xs text-cyan-300 font-mono tracking-wide uppercase">
              🌐 Learned Sequence Transfers & Field Flow Graph
            </span>
          </div>
          <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950 px-2.5 py-1 rounded-full border border-cyan-800">
            {activeTransfers.length} Sequence Transfer(s) Captured ({repetitionCount || 1} Cycle(s))
          </span>
        </div>

        {activeTransfers.length > 0 ? (
          <div className="flex flex-col gap-3 py-2">
            {activeTransfers.map((m: any, idx: number) => {
              const srcApp = m.source_app || "Source Application";
              const destApp = m.destination_app || "Target System";
              const srcLbl = m.source_label || m.source_entity || "Source Field";
              const destLbl = m.destination_label || m.destination_entity || "Target Field";

              return (
                <div key={idx} className="flex flex-col md:flex-row items-center justify-between gap-4 rounded-xl border border-slate-800/80 bg-slate-900/80 p-4 shadow-lg hover:border-cyan-500/40 transition-all duration-200">
                  {/* Left: Source App + Source Field */}
                  <div className="flex items-center gap-3 w-full md:w-5/12">
                    <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-cyan-500/20 text-xs font-bold text-cyan-300 font-mono border border-cyan-500/30 shrink-0">
                      {idx + 1}
                    </span>
                    <div className="flex flex-col min-w-0">
                      <span className="text-[10px] font-mono text-cyan-400 font-semibold uppercase tracking-wider">{srcApp}</span>
                      <span className="text-sm font-extrabold text-white truncate font-sans">{srcLbl}</span>
                    </div>
                  </div>

                  {/* Middle Arrow / Flow Indicator */}
                  <div className="flex items-center gap-2 text-cyan-400 font-mono text-xs shrink-0 py-1 md:py-0">
                    <span className="hidden md:inline font-bold tracking-widest text-cyan-400">─────────────────▶</span>
                    <span className="md:hidden font-bold text-cyan-400">▼</span>
                  </div>

                  {/* Right: Destination App + Target Field */}
                  <div className="flex items-center justify-between md:justify-start gap-3 w-full md:w-5/12">
                    <div className="flex flex-col min-w-0">
                      <span className="text-[10px] font-mono text-emerald-400 font-semibold uppercase tracking-wider">{destApp}</span>
                      <span className="text-sm font-extrabold text-emerald-300 truncate font-sans">{destLbl}</span>
                    </div>
                    {m.pasted_value && (
                      <span className="ml-auto text-[10px] font-mono text-amber-300 bg-slate-950 px-2.5 py-1 rounded border border-slate-800 truncate max-w-[140px]" title={m.pasted_value}>
                        "{m.pasted_value}"
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="p-5 text-xs text-slate-400 font-mono italic text-center">
            Waiting for telemetry transfers... Perform copy and paste actions in the live sandbox to observe dynamic process discovery.
          </div>
        )}
      </div>

      {/* Chronological Step Storyline Timeline */}
      <div className="flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">
            ⏱️ Observed Chronological Execution Flow
          </h3>
          <span className="text-[10px] font-mono text-slate-500">
            {activeSteps.length} Sequential Steps Captured
          </span>
        </div>

        <div className="flex flex-col gap-2.5">
          {activeSteps.map((step: any, idx: number) => (
            <div
              key={idx}
              className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/60 p-3.5 shadow-md transition-all duration-300 hover:border-purple-500/40"
            >
              <div className="flex items-center gap-3">
                <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-purple-500/10 text-purple-400 font-bold font-mono text-xs border border-purple-500/20 shrink-0">
                  {idx + 1}
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
      </div>

      {/* Optional Developer Inspection Drawer */}
      {showDeveloperDetails && (
        <div className="flex flex-col gap-4 rounded-xl border border-purple-500/30 bg-slate-950/90 p-5 shadow-xl animate-in slide-in-from-top-2 duration-200">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
            <div className="flex items-center gap-2">
              <Database className="h-4.5 w-4.5 text-purple-400" />
              <span className="font-bold text-xs text-purple-300 font-mono tracking-wide">
                ⚙️ Developer & Execution Metadata (Hidden from End-User)
              </span>
            </div>
            <span className="text-[10px] font-mono text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
              Debug Inspection Only
            </span>
          </div>

          <div className="flex flex-col gap-2.5">
            {activeTransfers.map((m: any, idx: number) => {
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
                        {isExpanded ? "Collapse Metadata" : "Inspect Identifiers"}
                      </span>
                      {isExpanded ? <ChevronUp className="h-4 w-4 text-purple-400" /> : <ChevronDown className="h-4 w-4 text-slate-400" />}
                    </div>
                  </button>

                  {isExpanded && (
                    <div className="flex flex-col gap-2.5 p-4 border-t border-slate-800/80 bg-slate-950/90 text-xs font-mono text-slate-300">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div className="flex flex-col gap-1 bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                          <span className="text-[10px] text-cyan-400 font-bold">SOURCE ENTITY KEY</span>
                          <span className="text-slate-100 font-semibold">{m.source_entity || "N/A"}</span>
                          <span className="text-[10px] text-slate-400">App: {m.source_app}</span>
                        </div>

                        <div className="flex flex-col gap-1 bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                          <span className="text-[10px] text-emerald-400 font-bold">DESTINATION ENTITY KEY</span>
                          <span className="text-slate-100 font-semibold">{m.destination_entity || "N/A"}</span>
                          <span className="text-[10px] text-slate-400">App: {m.destination_app}</span>
                        </div>
                      </div>

                      <div className="flex items-center justify-between text-[10px] text-slate-500 pt-1 border-t border-slate-900">
                        <span>Transfer ID: {m.transfer_id || "xfer-auto"}</span>
                        <span className="text-emerald-400 font-bold">✓ Internal Graph Link Active</span>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-950/90 p-4 text-[11px] font-mono text-slate-400">
            <span className="text-cyan-400 font-bold">Raw Discovered Graph JSON:</span>
            <pre className="mt-2 overflow-x-auto text-[10px] text-slate-500 leading-relaxed">
              {JSON.stringify({ workflow_id: workflowDNA?.workflow_id, mappings: activeTransfers, steps: activeSteps }, null, 2)}
            </pre>
          </div>
        </div>
      )}

      {/* Action Footer */}
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

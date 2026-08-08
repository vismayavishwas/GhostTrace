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
  observationSynthesis?: any;
  onProceed?: () => void;
}

export const WorkflowDNACollapse: React.FC<WorkflowDNACollapseProps> = ({
  workflowDNA,
  fieldMappings = [],
  chronologicalTransfers = [],
  observationSessionId = "",
  repetitionCount = 0,
  observationSynthesis,
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

  // Extract unique canonical field sequence template mappings by mapping identity tuple (source_app, source_label, dest_app, dest_label)
  const canonicalCycleMappings: any[] = [];
  const seenCanonicalKeys = new Set<string>();

  activeTransfers.forEach((m: any) => {
    const srcApp = m.source_app || "Source Application";
    const destApp = m.destination_app || "Target System";
    const srcLbl = m.source_label || m.source_entity || "Source Field";
    const destLbl = m.destination_label || m.destination_entity || "Target Field";

    const tupleKey = `${srcApp}::${srcLbl}::${destApp}::${destLbl}`;
    if (!seenCanonicalKeys.has(tupleKey)) {
      seenCanonicalKeys.add(tupleKey);
      canonicalCycleMappings.push({
        ...m,
        srcApp,
        destApp,
        srcLbl,
        destLbl,
      });
    }
  });

  // Approved workflow from synthesis or fallback to canonical cycle mappings
  // Deduplicate by canonical mapping tuple to always show ONE canonical cycle
  const rawApproved: any[] = observationSynthesis?.approved_workflow?.length
    ? observationSynthesis.approved_workflow
    : canonicalCycleMappings;

  const approvedSeenKeys = new Set<string>();
  const approvedWorkflow: any[] = [];
  rawApproved.forEach((m: any) => {
    const srcApp = m.source_app || "Source Application";
    const destApp = m.destination_app || "Target System";
    const srcLbl = m.source_label || m.source_entity || "Source Field";
    const destLbl = m.destination_label || m.destination_entity || "Target Field";
    const tupleKey = `${srcApp}::${srcLbl}::${destApp}::${destLbl}`;
    if (!approvedSeenKeys.has(tupleKey)) {
      approvedSeenKeys.add(tupleKey);
      approvedWorkflow.push({ ...m, srcApp, destApp, srcLbl, destLbl });
    }
  });

  const excludedOutliers: any[] = observationSynthesis?.excluded_outliers || [];

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
            {activeTransfers.length} Sequence Transfer(s) Captured ({repetitionCount} Cycle(s))
          </span>
        </div>

        {approvedWorkflow.length > 0 ? (
          <div className="flex flex-col gap-3 py-2">
            <div className="flex items-center justify-between border-b border-slate-800/60 pb-1.5 mb-1">
              <span className="text-[11px] font-mono font-bold text-purple-400 tracking-wider uppercase flex items-center gap-1.5">
                <span>LEARNED PATTERN ({approvedWorkflow.length}-Step Approved Sequence)</span>
              </span>
            </div>

            {approvedWorkflow.map((m: any, idx: number) => {
              const srcApp = m.source_app || m.srcApp || "Source Application";
              const destApp = m.destination_app || m.destApp || "Target System";
              const srcLbl = m.source_label || m.srcLbl || m.source_entity || "Source Field";
              const destLbl = m.destination_label || m.destLbl || m.destination_entity || "Target Field";

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

      {/* Chronological Execution Summary */}
      {(observationSynthesis?.historical_transfers?.length > 0 || activeSteps.length > 0) && (
        <div className="flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">
              ⏱️ Chronological Execution Flow
            </h3>
            <span className="text-[10px] font-mono text-slate-500">
              {observationSynthesis?.historical_transfers?.length || activeTransfers.length} Transfer(s) Across {repetitionCount} Cycle(s)
            </span>
          </div>

          <div className="flex flex-col gap-1.5">
            {(observationSynthesis?.historical_transfers || activeTransfers).map((t: any, idx: number) => {
              const srcLbl = t.source_label || t.source_entity || "Field";
              const destLbl = t.destination_label || t.destination_entity || "Field";
              const baselineLen = approvedWorkflow.length || 3;
              const cycleNum = Math.floor(idx / baselineLen) + 1;
              const stepInCycle = (idx % baselineLen) + 1;
              const isOutlier = excludedOutliers.some((o: any) => o.transfer_id && o.transfer_id === t.transfer_id);

              return (
                <div
                  key={idx}
                  className={`flex items-center justify-between rounded-lg border px-3 py-2 text-xs font-mono transition-all duration-200 ${
                    isOutlier
                      ? "border-amber-500/30 bg-amber-950/20 text-amber-300"
                      : "border-slate-800/60 bg-slate-950/50 text-slate-300 hover:border-slate-700"
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <span className={`flex h-5 w-5 items-center justify-center rounded text-[10px] font-bold border shrink-0 ${
                      isOutlier
                        ? "bg-amber-500/20 text-amber-400 border-amber-500/30"
                        : "bg-purple-500/15 text-purple-400 border-purple-500/25"
                    }`}>
                      {idx + 1}
                    </span>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded border ${
                      isOutlier
                        ? "bg-amber-950/40 text-amber-400 border-amber-500/20"
                        : "bg-cyan-950/40 text-cyan-400 border-cyan-500/20"
                    }`}>
                      C{cycleNum}.{stepInCycle}
                    </span>
                    <span className={isOutlier ? "text-amber-200" : "text-slate-200"}>
                      {srcLbl} → {destLbl}
                    </span>
                    {isOutlier && (
                      <span className="text-[9px] text-rose-400 font-bold bg-rose-950/50 px-1.5 py-0.5 rounded border border-rose-500/30">
                        OUTLIER
                      </span>
                    )}
                  </div>
                  {t.pasted_value && (
                    <span className="text-[10px] text-slate-500 truncate max-w-[120px]" title={t.pasted_value}>
                      "{t.pasted_value}"
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

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

          {excludedOutliers.length > 0 && (
            <div className="flex flex-col gap-2 rounded-xl border border-amber-500/30 bg-amber-950/20 p-4 font-mono text-xs">
              <span className="text-amber-400 font-bold text-[11px] uppercase tracking-wider flex items-center justify-between">
                <span>🚨 Excluded Outliers & Structural Deviations ({excludedOutliers.length})</span>
                <span className="text-[10px] text-rose-400 font-bold bg-rose-950/60 px-2 py-0.5 rounded border border-rose-500/30">
                  EXCLUDED_FROM_APPROVED_WORKFLOW
                </span>
              </span>
              <div className="flex flex-col gap-2 mt-1">
                {excludedOutliers.map((o: any, idx: number) => (
                  <div key={idx} className="flex flex-col gap-1.5 bg-slate-950/80 p-3 rounded-lg border border-amber-500/20 text-[11px]">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-amber-400 font-bold">Outlier #{idx + 1}:</span>
                        <span className="text-slate-100 font-bold">{o.source_entity} → {o.observed_destination}</span>
                        <span className="text-slate-400">(Expected: <strong className="text-emerald-400">{o.expected_destination || "N/A"}</strong>)</span>
                      </div>
                      <span className="text-[10px] text-amber-300 font-bold bg-amber-950/60 px-2 py-0.5 rounded border border-amber-500/30">
                        {o.status || "EXCLUDED_FROM_APPROVED_WORKFLOW"}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-[10px] text-slate-400 pt-1 border-t border-slate-900 flex-wrap">
                      <span>ID: <strong className="text-slate-300">{o.transfer_id || `xfer-${idx+1}`}</strong></span>
                      {o.pasted_value && <span>Pasted Value: <strong className="text-amber-300">"{o.pasted_value}"</strong></span>}
                      {o.cycle && <span>Cycle: <strong className="text-cyan-400">{o.cycle}</strong></span>}
                      {o.reason && <span>Reason: <strong className="text-rose-300">{o.reason}</strong></span>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="rounded-xl border border-slate-800 bg-slate-950/90 p-4 text-[11px] font-mono text-slate-400">
            <span className="text-cyan-400 font-bold">Raw Discovered Graph JSON:</span>
            <pre className="mt-2 overflow-x-auto text-[10px] text-slate-500 leading-relaxed">
              {JSON.stringify({ workflow_id: workflowDNA?.workflow_id, mappings: activeTransfers, steps: activeSteps, excluded_outliers: excludedOutliers }, null, 2)}
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

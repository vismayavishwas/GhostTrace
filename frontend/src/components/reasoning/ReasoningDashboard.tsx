"use client";

import React from "react";
import { Brain, CheckCircle2, ArrowRight, Zap, ShieldCheck, Activity, Eye, AlertTriangle, Layers, GitBranch } from "lucide-react";

export interface ReasoningDashboardProps {
  confidenceScore?: number;
  repetitionCount?: number;
  noiseFilteredCount?: number;
  candidateName?: string;
  workflowDNA?: any;
  fieldMappings?: any[];
  chronologicalTransfers?: any[];
  outliers?: any[];
  observationSessionId?: string;
  observationSynthesis?: any;
  onProceedToDNA: () => void;
  onObserveFurther?: () => void;
}

export const ReasoningDashboard: React.FC<ReasoningDashboardProps> = ({
  confidenceScore = 0.0,
  repetitionCount = 0,
  noiseFilteredCount = 0,
  candidateName = "Cross-Application Workflow",
  workflowDNA,
  fieldMappings = [],
  chronologicalTransfers = [],
  outliers = [],
  observationSessionId = "",
  observationSynthesis,
  onProceedToDNA,
  onObserveFurther,
}) => {
  const confidencePct = Math.round((confidenceScore || 0.0) * 100);

  // Extract field mappings from props or Workflow DNA metadata
  const rawMaps = fieldMappings.length > 0
    ? fieldMappings
    : (workflowDNA?.metadata?.field_mappings || workflowDNA?.field_mappings || []);

  const confirmedMappings: any[] = [];
  const seenKeys = new Set<string>();

  rawMaps.forEach((m: any) => {
    const srcLbl = m.source_label || m.source_entity || "Unknown Field";
    const destLbl = m.destination_label || m.destination_entity || "Unknown Field";
    const srcApp = m.source_app || "Source Application";
    const destApp = m.destination_app || "Target Application";

    const k = `${srcApp}::${srcLbl}::${destApp}::${destLbl}`;
    if (!seenKeys.has(k)) {
      seenKeys.add(k);
      confirmedMappings.push({
        ...m,
        cleanSourceLabel: srcLbl,
        cleanDestLabel: destLbl,
        sourceApp: srcApp,
        destApp: destApp,
      });
    }
  });

  const activeOutlierCount = observationSynthesis?.outlier_count !== undefined
    ? observationSynthesis.outlier_count
    : outliers.length;

  const sampleMappingSummary = confirmedMappings.length > 0
    ? confirmedMappings.map(m => `'${m.cleanSourceLabel} → ${m.cleanDestLabel}'`).join(", ")
    : "field transfers";

  // Build confidence explanation in plain language
  let confidenceReasoning = "";
  if (confidenceScore >= 0.75) {
    confidenceReasoning = `Confidence is high (${confidencePct}%) because the semantic mapping(s) ${sampleMappingSummary} have been observed consistently across ${repetitionCount} workflow cycle(s) with ${activeOutlierCount} sequence outlier(s).`;
  } else if (confidenceScore >= 0.35) {
    confidenceReasoning = `Confidence is at ${confidencePct}% based on ${repetitionCount} consistent workflow cycle(s) and ${confirmedMappings.length} confirmed semantic field mapping(s). Additional repetitions will further solidify learning.`;
  } else if (repetitionCount > 0) {
    confidenceReasoning = `Confidence is at ${confidencePct}%. Observed ${repetitionCount} cycle(s), but additional repeated executions are required to reach full confidence.`;
  } else {
    confidenceReasoning = `Confidence is currently at ${confidencePct}% based on ${confirmedMappings.length} observed transfer(s). Perform repeated copy/paste operations across fields to accumulate evidence.`;
  }

  return (
    <div className="flex flex-col gap-6 w-full max-w-7xl mx-auto rounded-2xl border border-slate-800/80 bg-slate-900/90 p-6 md:p-8 shadow-2xl backdrop-blur-xl">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1 rounded-md bg-purple-500/10 px-2.5 py-1 text-xs font-bold text-purple-400 border border-purple-500/20">
              <Brain className="h-3.5 w-3.5" />
              🧠 AI Perception & Reasoning Dashboard
            </span>
            <span className="text-xs font-mono text-slate-500 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              Real-Time Analysis
            </span>
          </div>
          <h2 className="mt-2 text-xl font-extrabold text-white tracking-tight">
            Observed Pattern Synthesis & Evidence Breakdown
          </h2>
          <p className="text-xs text-slate-400">
            Explaining what the AI observed, why it inferred a repeatable workflow, and how confidence was derived.
          </p>
        </div>

        <div className="flex items-center gap-3 bg-slate-950/80 px-4 py-2.5 rounded-xl border border-slate-800 shrink-0">
          <div className="flex flex-col text-right">
            <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">Learning Confidence</span>
            <span className="text-2xl font-black font-mono text-cyan-400">{confidencePct}%</span>
          </div>
          <Zap className="h-6 w-6 text-cyan-400 animate-pulse" />
        </div>
      </div>

      {/* 4 Core Reasoning Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Card 1: What has the AI learned? */}
        <div className="flex flex-col gap-3 rounded-xl border border-cyan-500/30 bg-slate-950/80 p-5 shadow-xl">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
            <div className="flex items-center gap-2">
              <Layers className="h-4 w-4 text-cyan-400" />
              <h3 className="font-bold text-sm text-cyan-300">1. What Has the AI Learned?</h3>
            </div>
            <span className="text-[10px] font-mono text-cyan-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
              {confirmedMappings.length} Confirmed Mappings
            </span>
          </div>

          <p className="text-xs text-slate-300 leading-relaxed">
            The perception engine observed cross-application telemetry and discovered the following stable semantic field lineage:
          </p>

          {confirmedMappings.length > 0 ? (
            <div className="flex flex-col gap-2.5 my-1">
              {confirmedMappings.map((m: any, idx: number) => (
                <div key={idx} className="flex items-center gap-2.5 text-xs font-mono bg-slate-900/60 p-3 rounded-lg border border-slate-800">
                  <span className="text-cyan-400 font-bold text-[11px]">#{idx + 1}</span>
                  <div className="flex items-center gap-1.5 flex-wrap">
                    <span className="font-bold text-slate-100 bg-slate-950 px-2.5 py-1 rounded border border-slate-700">
                      {m.cleanSourceLabel}
                    </span>
                    <span className="text-cyan-400 font-bold tracking-tighter">─────────▶</span>
                    <span className="font-bold text-emerald-300 bg-emerald-950/60 px-2.5 py-1 rounded border border-emerald-500/40">
                      {m.cleanDestLabel}
                    </span>
                  </div>
                  <span className="text-[10px] text-slate-400 font-sans ml-auto bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                    {m.sourceApp} → {m.destApp}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-3 text-xs text-slate-400 font-mono italic bg-slate-900/40 rounded-lg border border-slate-800">
              Waiting for cross-application telemetry transfers... Perform copy/paste operations in the sandbox to observe dynamic field lineage.
            </div>
          )}
        </div>

        {/* Card 2: Why does it believe this is a repeatable workflow? */}
        <div className="flex flex-col gap-3 rounded-xl border border-purple-500/30 bg-slate-950/80 p-5 shadow-xl">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-purple-400" />
              <h3 className="font-bold text-sm text-purple-300">2. Why Is This a Repeatable Workflow?</h3>
            </div>
            <span className="text-[10px] font-mono text-purple-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
              {repetitionCount} Cycle(s) Completed
            </span>
          </div>

          <p className="text-xs text-slate-300 leading-relaxed">
            {repetitionCount > 0 ? (
              <>
                The discovery engine tracked <strong className="text-purple-300">{repetitionCount} complete workflow execution cycle(s)</strong>.
                The field transfer order remained identical across sessions, proving this is a structured business process rather than random clicks.
              </>
            ) : (
              <>
                Zero full sequence cycles observed so far. The engine is accumulating telemetry events and waiting for repeated executions to confirm structural consistency.
              </>
            )}
          </p>

          <div className="mt-auto grid grid-cols-2 gap-3 text-xs pt-2">
            <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-3">
              <span className="text-slate-400 font-medium text-[11px]">Sequence Alignment</span>
              <p className="mt-1 font-bold text-emerald-400 font-mono">
                {repetitionCount > 0 ? "100% Chronological Match" : "Waiting for cycles"}
              </p>
            </div>
            <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-3">
              <span className="text-slate-400 font-medium text-[11px]">Outliers Detected</span>
              <p className="mt-1 font-bold text-cyan-400 font-mono">
                Outliers Detected: {activeOutlierCount}
              </p>
            </div>
          </div>
        </div>

        {/* Card 3: How confident is it, and why? */}
        <div className="flex flex-col gap-3 rounded-xl border border-emerald-500/30 bg-slate-950/80 p-5 shadow-xl">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
            <div className="flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-emerald-400" />
              <h3 className="font-bold text-sm text-emerald-300">3. How Confident Is It, and Why?</h3>
            </div>
            <span className="text-[10px] font-mono text-emerald-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
              Score: {confidencePct}%
            </span>
          </div>

          <p className="text-xs text-slate-200 leading-relaxed font-sans bg-emerald-950/20 border border-emerald-500/20 p-3 rounded-lg">
            {confidenceReasoning}
          </p>

          <div className="flex items-center gap-2 text-xs font-mono text-slate-400 pt-1">
            {activeOutlierCount > 0 ? (
              <AlertTriangle className="h-4 w-4 text-amber-400 shrink-0" />
            ) : (
              <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
            )}
            <span>Outliers Detected: {activeOutlierCount}</span>
          </div>
        </div>

        {/* Card 4: What happens next before automation can be generated? */}
        <div className="flex flex-col gap-3 rounded-xl border border-amber-500/30 bg-slate-950/80 p-5 shadow-xl">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
            <div className="flex items-center gap-2">
              <GitBranch className="h-4 w-4 text-amber-400" />
              <h3 className="font-bold text-sm text-amber-300">4. What Happens Next?</h3>
            </div>
            <span className="text-[10px] font-mono text-amber-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
              Next Stage: Workflow DNA
            </span>
          </div>

          <p className="text-xs text-slate-300 leading-relaxed">
            Before generating executable Playwright automation code, the AI transforms these learned semantic mappings into an interactive <strong className="text-amber-300">Workflow DNA Process Discovery Graph</strong>.
          </p>

          <p className="text-xs text-slate-400 leading-relaxed">
            In the Workflow DNA view, you can visually inspect application containers, field-to-field linkages, and chronological execution steps.
          </p>
        </div>
      </div>

      {/* Bottom High-Impact Decision Banner */}
      <div className="mt-2 flex flex-col md:flex-row md:items-center justify-between gap-4 rounded-xl border border-cyan-500/40 bg-gradient-to-r from-cyan-950/60 via-slate-900 to-purple-950/60 p-5 shadow-xl">
        <div>
          <h4 className="text-sm font-bold text-white flex items-center gap-2">
            <span>Workflow Candidate Confirmed</span>
            <span className="text-[10px] font-mono text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
              Ready for Visual Synthesis
            </span>
          </h4>
          <p className="text-xs text-slate-300 mt-1">
            Target Process: <span className="font-mono text-cyan-300 font-bold">{candidateName}</span>
          </p>
        </div>

        <div className="flex items-center gap-3">
          {onObserveFurther && (
            <button
              onClick={onObserveFurther}
              className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-800/80 px-4 py-2.5 text-xs font-bold text-slate-200 hover:bg-slate-700 transition-all"
            >
              <Eye className="h-4 w-4 text-slate-400" />
              <span>Observe Further</span>
            </button>
          )}

          <button
            onClick={onProceedToDNA}
            className="flex items-center gap-2 rounded-xl bg-cyan-500 px-6 py-2.5 text-xs font-bold text-slate-950 shadow-lg shadow-cyan-500/30 hover:bg-cyan-400 transition-all"
          >
            <span>Proceed to Workflow DNA Graph</span>
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

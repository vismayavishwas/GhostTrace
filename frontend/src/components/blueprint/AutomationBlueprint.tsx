"use client";

import React, { useState, useEffect } from "react";
import { ArrowRight, FileText, CheckCircle2, Cpu, Database, Send, Bell } from "lucide-react";

export interface BlueprintStep {
  step_index: number;
  phase: "INPUT" | "VALIDATE" | "EXTRACT" | "TRANSFORM" | "SUBMIT" | "NOTIFY";
  title: string;
  detail: string;
  icon: any;
}

export interface AutomationBlueprintProps {
  onProceedToDeploy: () => void;
  workflowDNA?: any;
  observationSynthesis?: any;
}

export const AutomationBlueprint: React.FC<AutomationBlueprintProps> = ({
  onProceedToDeploy,
  workflowDNA,
  observationSynthesis,
}) => {
  const [activeStepIdx, setActiveStepIdx] = useState<number>(-1);

  // Extract canonical approved 1-cycle mappings
  const rawApproved: any[] = observationSynthesis?.approved_workflow?.length
    ? observationSynthesis.approved_workflow
    : (workflowDNA?.field_mappings || []);

  const approvedSeenKeys = new Set<string>();
  const canonicalMappings: any[] = [];

  rawApproved.forEach((m: any, idx: number) => {
    const srcApp = m.source_app || "Source Application";
    const destApp = m.destination_app || "Target Application";
    const srcLbl = m.source_label || m.source_entity || "Source Field";
    const destLbl = m.destination_label || m.destination_entity || "Target Field";
    const varName = m.variable_name || `current_record.field_${idx + 1}`;
    const srcSel = m.source_selector || "";
    const destSel = m.destination_selector || "";

    const tupleKey = `${srcApp}::${srcLbl}::${destApp}::${destLbl}`;
    if (!approvedSeenKeys.has(tupleKey)) {
      approvedSeenKeys.add(tupleKey);
      canonicalMappings.push({ srcApp, destApp, srcLbl, destLbl, varName, srcSel, destSel });
    }
  });

  useEffect(() => {
    const handleReplaySync = (e: any) => {
      if (e.detail && e.detail.stepIndex !== undefined) {
        setActiveStepIdx(e.detail.stepIndex - 1);
      }
    };

    if (typeof window !== "undefined") {
      window.addEventListener("ghosttrace:replay-step", handleReplaySync);
    }

    return () => {
      if (typeof window !== "undefined") {
        window.removeEventListener("ghosttrace:replay-step", handleReplaySync);
      }
    };
  }, []);

  return (
    <div className="flex flex-col gap-6 rounded-2xl border border-slate-800/80 bg-slate-900/90 p-6 shadow-2xl backdrop-blur-xl">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
        <div>
          <span className="inline-flex items-center gap-1.5 rounded-md bg-purple-500/10 px-2.5 py-1 text-xs font-bold text-purple-400 border border-purple-500/20">
            📐 Parameterized Automation Architecture
          </span>
          <h2 className="mt-2 text-lg font-bold text-white">Automation Blueprint Spec</h2>
          <p className="text-xs text-slate-400">Executable knowledge graph derived strictly from canonical telemetry cycles.</p>
        </div>

        <button
          suppressHydrationWarning
          onClick={onProceedToDeploy}
          disabled={canonicalMappings.length === 0}
          className={`flex items-center gap-2 rounded-xl px-5 py-2.5 text-xs font-bold shadow-lg transition-all ${
            canonicalMappings.length > 0
              ? "bg-gradient-to-r from-cyan-500 to-purple-500 text-slate-950 shadow-cyan-500/25 hover:brightness-110"
              : "bg-slate-800 text-slate-500 cursor-not-allowed"
          }`}
        >
          <span>Proceed to Ghost Replay Simulation 👻</span>
          <ArrowRight className="h-4 w-4" />
        </button>
      </div>

      {/* Canonical Approved Mappings derived from Approved Workflow DNA */}
      {canonicalMappings.length > 0 ? (
        <div className="flex flex-col gap-3 rounded-xl border border-purple-500/30 bg-purple-950/20 p-4">
          <div className="flex items-center justify-between border-b border-purple-500/20 pb-2">
            <span className="text-xs font-mono font-bold text-purple-300 uppercase tracking-wider">
              Learned Parameterized Workflow Steps ({canonicalMappings.length} Actions)
            </span>
            <span className="text-[10px] font-mono text-purple-400">
              Canonical Telemetry • Outliers Excluded
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {canonicalMappings.map((m, idx) => (
              <div
                key={idx}
                className={`flex flex-col gap-1.5 rounded-lg border p-3 text-xs transition ${
                  idx === activeStepIdx
                    ? "border-emerald-500/70 bg-emerald-950/40 text-emerald-200 shadow-lg shadow-emerald-500/20"
                    : "border-slate-800 bg-slate-950/80 text-slate-200"
                }`}
              >
                <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
                  <span>STEP #{idx + 1}</span>
                  <span className="text-cyan-400 font-bold font-mono">{m.varName}</span>
                </div>
                <div className="flex items-center justify-between font-bold text-slate-200 mt-1">
                  <span className="text-cyan-300">{m.srcLbl}</span>
                  <span className="text-slate-500">➔</span>
                  <span className="text-emerald-300">{m.destLbl}</span>
                </div>
                <div className="text-[9px] font-mono text-slate-400 mt-0.5 truncate">
                  Source: {m.srcApp} {m.srcSel ? `(${m.srcSel})` : ""}
                </div>
                <div className="text-[9px] font-mono text-slate-400 truncate">
                  Target: {m.destApp} {m.destSel ? `(${m.destSel})` : ""}
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center p-8 rounded-xl border border-dashed border-slate-800 bg-slate-950/40 text-center">
          <Cpu className="h-8 w-8 text-slate-600 animate-pulse mb-2" />
          <h3 className="text-sm font-bold text-slate-300">Waiting for workflow DNA...</h3>
          <p className="text-xs text-slate-500 mt-1">Perform 3 manual records in the sandbox to generate the parameterized blueprint.</p>
        </div>
      )}
    </div>
  );
};

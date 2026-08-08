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

const BLUEPRINT_STEPS: BlueprintStep[] = [
  { step_index: 1, phase: "INPUT", title: "Listen for New Gmail Invoice", detail: "PDF attachment trigger", icon: FileText },
  { step_index: 2, phase: "VALIDATE", title: "Validate Schema & Vendor ID", detail: "Matches active vendor DB", icon: CheckCircle2 },
  { step_index: 3, phase: "EXTRACT", title: "Extract Line Item Metadata", detail: "Parse total amount & tax", icon: Cpu },
  { step_index: 4, phase: "TRANSFORM", title: "Format SAP ERP Payload", detail: "Map fields to ERP schema", icon: Database },
  { step_index: 5, phase: "SUBMIT", title: "Post Invoice to SAP ERP", detail: "Automated form entry", icon: Send },
  { step_index: 6, phase: "NOTIFY", title: "Notify Finance Team Slack", detail: "Post completion receipt", icon: Bell },
];

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
  const [dynamicSteps, setDynamicSteps] = useState<BlueprintStep[]>(BLUEPRINT_STEPS);

  // Extract canonical approved 1-cycle mappings
  const rawApproved: any[] = observationSynthesis?.approved_workflow?.length
    ? observationSynthesis.approved_workflow
    : (workflowDNA?.field_mappings || []);

  const approvedSeenKeys = new Set<string>();
  const canonicalMappings: any[] = [];

  rawApproved.forEach((m: any) => {
    const srcApp = m.source_app || "PDF INVOICE SOURCE";
    const destApp = m.destination_app || "SAP ERP FINANCIALS";
    const srcLbl = m.source_label || m.source_entity || "Source Field";
    const destLbl = m.destination_label || m.destination_entity || "Target Field";
    const tupleKey = `${srcApp}::${srcLbl}::${destApp}::${destLbl}`;
    if (!approvedSeenKeys.has(tupleKey)) {
      approvedSeenKeys.add(tupleKey);
      canonicalMappings.push({ srcApp, destApp, srcLbl, destLbl });
    }
  });

  useEffect(() => {
    import("@/lib/api").then(({ fetchGraphState }) => {
      fetchGraphState().then((state) => {
        if (state) {
          const srcApp = state.business_process?.workflow_name || state.candidate_name || "Source Application";
          const steps: BlueprintStep[] = [
            { step_index: 1, phase: "INPUT", title: `Ingest Stream from ${srcApp}`, detail: "Live browser interaction trigger", icon: FileText },
            { step_index: 2, phase: "VALIDATE", title: "Validate Schema & Semantic Entities", detail: "Positions & metadata signals checked", icon: CheckCircle2 },
            { step_index: 3, phase: "EXTRACT", title: "Extract Semantic Field Intent", detail: "Abstract intent window aggregation", icon: Cpu },
            { step_index: 4, phase: "TRANSFORM", title: "Format Automated Playwright Script", detail: "Target field mapping & locator synthesis", icon: Database },
            { step_index: 5, phase: "SUBMIT", title: "Execute Cross-Application Automation", detail: "Autonomous form entry & replay", icon: Send },
            { step_index: 6, phase: "NOTIFY", title: "Post Audit Log & Status Receipt", detail: "Enterprise process timeline update", icon: Bell },
          ];
          setDynamicSteps(steps);
        }
      });
    });

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
            📐 Automation Architecture
          </span>
          <h2 className="mt-2 text-lg font-bold text-white">Automation Blueprint Spec</h2>
          <p className="text-xs text-slate-400">High-level semantic blueprint bridging Workflow DNA to Playwright Compiler.</p>
        </div>

        <button
          suppressHydrationWarning
          onClick={onProceedToDeploy}
          className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-purple-500 px-5 py-2.5 text-xs font-bold text-slate-950 shadow-lg shadow-cyan-500/25 transition-all hover:brightness-110"
        >
          <span>Proceed to Ghost Replay Simulation 👻</span>
          <ArrowRight className="h-4 w-4" />
        </button>
      </div>

      {/* Canonical Approved Mappings derived from Approved Workflow DNA */}
      {canonicalMappings.length > 0 && (
        <div className="flex flex-col gap-3 rounded-xl border border-purple-500/30 bg-purple-950/20 p-4">
          <div className="flex items-center justify-between border-b border-purple-500/20 pb-2">
            <span className="text-xs font-mono font-bold text-purple-300 uppercase tracking-wider">
              Approved Canonical Automation Actions (1-Cycle Blueprint Sequence)
            </span>
            <span className="text-[10px] font-mono text-purple-400">
              {canonicalMappings.length} Approved Action(s) • Outliers Excluded
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {canonicalMappings.map((m, idx) => (
              <div key={idx} className="flex flex-col gap-1 rounded-lg border border-slate-800 bg-slate-950/80 p-3 text-xs">
                <div className="flex items-center justify-between text-[10px] font-mono text-slate-500">
                  <span>ACTION #{idx + 1}</span>
                  <span className="text-emerald-400 font-bold">COPY ➔ PASTE</span>
                </div>
                <div className="flex items-center justify-between font-bold text-slate-200 mt-1">
                  <span className="text-cyan-300">{m.srcLbl}</span>
                  <span className="text-slate-500">➔</span>
                  <span className="text-emerald-300">{m.destLbl}</span>
                </div>
                <div className="text-[9px] font-mono text-slate-400 mt-1">
                  {m.srcApp} ➔ {m.destApp}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Blueprint Steps Flow (Glowing sync during Ghost Replay) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {dynamicSteps.map((step, idx) => {
          const Icon = step.icon;

          const isActive = idx === activeStepIdx;
          const isDone = idx < activeStepIdx;

          return (
            <div
              key={step.step_index}
              className={`flex flex-col justify-between rounded-xl border p-4 shadow-md backdrop-blur-sm transition ${
                isActive
                  ? "border-emerald-500/70 bg-emerald-950/30 text-emerald-200 shadow-xl shadow-emerald-500/20 animate-pulse"
                  : isDone
                  ? "border-emerald-500/30 bg-slate-950/80 text-slate-200"
                  : "border-slate-800 bg-slate-950/60 text-slate-400"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className={`rounded-md px-2 py-0.5 text-[10px] font-mono font-bold ${
                  isActive ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40" : "bg-slate-800 text-cyan-400"
                }`}>
                  PHASE {step.step_index}: {step.phase}
                </span>
                <Icon className={`h-4 w-4 ${isActive ? "text-emerald-400 animate-bounce" : "text-purple-400"}`} />
              </div>
              <h4 className="mt-3 text-xs font-bold text-slate-100">{step.title}</h4>
              <p className="mt-1 text-[11px] text-slate-400">{step.detail}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
};

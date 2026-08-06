"use client";

import React from "react";
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
}

export const AutomationBlueprint: React.FC<AutomationBlueprintProps> = ({ onProceedToDeploy }) => {
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
          onClick={onProceedToDeploy}
          className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-purple-500 px-5 py-2.5 text-xs font-bold text-slate-950 shadow-lg shadow-cyan-500/25 transition-all hover:brightness-110"
        >
          <span>Compile & Deploy Agent</span>
          <ArrowRight className="h-4 w-4" />
        </button>
      </div>

      {/* Blueprint Steps Flow */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {BLUEPRINT_STEPS.map((step) => {
          const Icon = step.icon;
          return (
            <div
              key={step.step_index}
              className="flex flex-col justify-between rounded-xl border border-slate-800 bg-slate-950/60 p-4 shadow-md backdrop-blur-sm"
            >
              <div className="flex items-center justify-between">
                <span className="rounded-md bg-slate-800 px-2 py-0.5 text-[10px] font-mono font-bold text-cyan-400">
                  PHASE {step.step_index}: {step.phase}
                </span>
                <Icon className="h-4 w-4 text-purple-400" />
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

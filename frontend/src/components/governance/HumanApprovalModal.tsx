"use client";

import React from "react";
import { ShieldCheck, CheckCircle2, ArrowRight, X, Clock, Database, Lock } from "lucide-react";

export interface HumanApprovalModalProps {
  workflowName?: string;
  canonicalCycles?: number;
  outlierCount?: number;
  learnedSteps?: number;
  remainingRecords?: number;
  onApprove: () => void;
  onReject?: () => void;
}

export const HumanApprovalModal: React.FC<HumanApprovalModalProps> = ({
  workflowName = "Learned Process Automation Workflow",
  canonicalCycles = 3,
  outlierCount = 0,
  learnedSteps = 3,
  remainingRecords = 5,
  onApprove,
  onReject,
}) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/90 p-4 backdrop-blur-xl animate-fade-in">
      <div className="w-full max-w-xl rounded-2xl border border-cyan-500/30 bg-slate-900/95 p-6 shadow-2xl backdrop-blur-2xl">
        {/* Header */}
        <div className="flex items-start justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-cyan-500/10 p-3 text-cyan-400 border border-cyan-500/20 shadow-md">
              <ShieldCheck className="h-6 w-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="rounded-md bg-purple-500/10 px-2 py-0.5 text-[10px] font-bold text-purple-400 border border-purple-500/20">
                  Governance Authorization
                </span>
                <h2 className="text-lg font-bold text-white">Human Approval & Governance Gate</h2>
              </div>
              <p className="text-xs text-slate-400">Authorize GhostTrace to execute the learned workflow against remaining records.</p>
            </div>
          </div>

          {onReject && (
            <button onClick={onReject} className="rounded-lg p-1.5 text-slate-500 hover:bg-slate-800 hover:text-slate-300">
              <X className="h-5 w-5" />
            </button>
          )}
        </div>

        {/* Spec Overview Card */}
        <div className="mt-5 flex flex-col gap-4">
          <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
            <h3 className="text-sm font-bold text-cyan-400">{workflowName}</h3>
            <p className="text-xs text-slate-300 mt-1">Learned from {canonicalCycles} canonical manual execution cycles ({outlierCount} outliers excluded)</p>
          </div>

          {/* Key Audit Checklist */}
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="flex items-center gap-2.5 rounded-lg border border-slate-800/80 bg-slate-950/40 p-3">
              <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
              <div>
                <span className="text-[10px] text-slate-400 block">Learned Sequence</span>
                <span className="font-semibold text-slate-200">{learnedSteps} Parameterized Steps</span>
              </div>
            </div>

            <div className="flex items-center gap-2.5 rounded-lg border border-slate-800/80 bg-slate-950/40 p-3">
              <Clock className="h-4 w-4 text-cyan-400 shrink-0" />
              <div>
                <span className="text-[10px] text-slate-400 block">Canonical Cycles</span>
                <span className="font-semibold font-mono text-cyan-400">{canonicalCycles} Verified Cycles</span>
              </div>
            </div>

            <div className="flex items-center gap-2.5 rounded-lg border border-slate-800/80 bg-slate-950/40 p-3">
              <Database className="h-4 w-4 text-purple-400 shrink-0" />
              <div>
                <span className="text-[10px] text-slate-400 block">Remaining Workload</span>
                <span className="font-semibold text-slate-200">{remainingRecords} Target Record(s)</span>
              </div>
            </div>

            <div className="flex items-center gap-2.5 rounded-lg border border-slate-800/80 bg-slate-950/40 p-3">
              <Lock className="h-4 w-4 text-emerald-400 shrink-0" />
              <div>
                <span className="text-[10px] text-slate-400 block">Outlier Filtering</span>
                <span className="font-semibold text-emerald-400">{outlierCount} Excluded Outliers</span>
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="mt-6 flex items-center justify-between border-t border-slate-800/80 pt-4">
          <span className="text-[11px] text-slate-500 font-mono">Status: Awaiting Manager Approval</span>
          <div className="flex items-center gap-3">
            {onReject && (
              <button
                onClick={onReject}
                className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-2.5 text-xs font-bold text-slate-300 hover:bg-slate-800"
              >
                Reject & Discard
              </button>
            )}
            <button
              onClick={onApprove}
              className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-purple-500 px-6 py-2.5 text-xs font-black text-slate-950 shadow-lg shadow-cyan-500/25 hover:brightness-110 transition-all"
            >
              <span>Approve & Authorize Deployment</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

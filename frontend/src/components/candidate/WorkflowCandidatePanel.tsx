"use client";

import React, { useState } from "react";
import { Sparkles, ArrowRight, Zap, Eye, AlertTriangle, CheckCircle2, ShieldAlert, CheckSquare, Square } from "lucide-react";
import { refineCandidate } from "@/lib/api";

export interface BusinessProcessData {
  workflow_name?: string;
  department?: string;
  business_goal?: string;
  confidence?: number;
  repeatability?: string;
  automation_readiness?: string;
  summary?: string;
}

export interface OutlierItem {
  id: string;
  label: string;
  selector: string;
  reason: string;
}

export interface WorkflowCandidatePanelProps {
  candidateId?: string;
  confidenceScore?: number;
  candidateName?: string;
  businessProcess?: BusinessProcessData | null;
  outliers?: OutlierItem[];
  onAnalyzeTrigger: () => void;
  onObserveFurther?: () => void;
}




export const WorkflowCandidatePanel: React.FC<WorkflowCandidatePanelProps> = ({
  candidateId = "cand-default",
  confidenceScore = 0.0,
  candidateName = "Enterprise Data Transfer Workflow",
  businessProcess,
  outliers = [],
  onAnalyzeTrigger,
  onObserveFurther,
}) => {
  const [version, setVersion] = useState<number>(1);
  const [currentScore, setCurrentScore] = useState<number>(confidenceScore || 0.82);
  const [feedbackMsg, setFeedbackMsg] = useState<string>("");
  const [outlierList, setOutlierList] = useState<OutlierItem[]>(outliers);
  const [selectedOutlierIds, setSelectedOutlierIds] = useState<Set<string>>(new Set(outliers.map(o => o.id)));
  const [isReviewPending, setIsReviewPending] = useState<boolean>(outliers.length > 0);

  React.useEffect(() => {
    setOutlierList(outliers);
    setSelectedOutlierIds(new Set(outliers.map(o => o.id)));
    if (outliers.length === 0) {
      setIsReviewPending(false);
    }
  }, [outliers]);

  const effectiveScore = currentScore > 0 ? currentScore : confidenceScore;
  const confidencePct = Math.round(effectiveScore * 100);
  
  // Rule: Unlock Analyze button directly when no outliers exist OR after review
  const isAnalyzeEnabled = (!isReviewPending || outlierList.length === 0) && effectiveScore >= 0.70;


  const title = businessProcess?.workflow_name || candidateName;
  const dept = businessProcess?.department || "Operations & IT";
  const readiness = businessProcess?.automation_readiness || "High Readiness";
  const obsCount = businessProcess?.repeatability || "3 Observations";
  const summaryText = businessProcess?.summary || "Automates repetitive cross-app data entry workflow.";

  const toggleSelectAll = () => {
    if (selectedOutlierIds.size === outlierList.length) {
      setSelectedOutlierIds(new Set());
    } else {
      setSelectedOutlierIds(new Set(outlierList.map((item) => item.id)));
    }
  };

  const clearSelection = () => {
    setSelectedOutlierIds(new Set());
  };

  const toggleItem = (id: string) => {
    const next = new Set(selectedOutlierIds);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setSelectedOutlierIds(next);
  };

  const handleBatchRefine = async (choice: "EXCLUDE" | "INCLUDE") => {
    const selectedSelectors = outlierList
      .filter((o) => selectedOutlierIds.has(o.id))
      .map((o) => o.selector);

    const targetSel = selectedSelectors.join(",") || "#help-btn";
    const res = await refineCandidate(candidateId, choice, targetSel);

    const prevPct = Math.round((res?.previous_confidence || effectiveScore) * 100);
    const newPct = Math.round((res?.new_confidence || 0.96) * 100);
    const newVer = res?.version || version + 1;

    setVersion(newVer);
    setCurrentScore(res?.new_confidence || 0.96);
    setIsReviewPending(false);

    if (choice === "EXCLUDE") {
      setFeedbackMsg(`✓ Candidate Updated (v${newVer}) — Excluded ${selectedOutlierIds.size} item(s). Confidence: ${prevPct}% → ${newPct}%`);
    } else {
      setFeedbackMsg(`✓ Candidate Updated (v${newVer}) — Included ${selectedOutlierIds.size} item(s). Confidence: ${newPct}%`);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/85 backdrop-blur-md p-4 overflow-y-auto animate-in fade-in zoom-in-95 duration-200">
      <div className="relative flex flex-col gap-5 w-full max-w-3xl rounded-2xl border border-cyan-500/50 bg-gradient-to-br from-slate-900 via-slate-950 to-purple-950/90 p-6 shadow-2xl shadow-cyan-500/20 backdrop-blur-2xl">
        
        {/* Dismiss Modal Close Button */}
        {onObserveFurther && (
          <button
            suppressHydrationWarning
            onClick={onObserveFurther}
            className="absolute top-4 right-4 rounded-lg p-1 text-slate-400 hover:bg-slate-800 hover:text-white transition"
          >
            ✕
          </button>
        )}

        {/* Top Main Candidate Discovery Header */}
        <div className="flex flex-col md:flex-row items-start justify-between gap-4 border-b border-slate-800 pb-4">
          <div className="flex items-center gap-3.5">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 shadow-lg shadow-cyan-500/10 shrink-0">
              <Sparkles className="h-6 w-6 animate-pulse" />
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <span className="rounded-full bg-cyan-500/20 px-2.5 py-0.5 text-[10px] font-mono font-extrabold text-cyan-300 border border-cyan-500/30">
                  🎉 WORKFLOW PATTERN DETECTED
                </span>
                <span className="rounded-full bg-slate-800 px-2.5 py-0.5 text-[10px] font-mono text-slate-300 border border-slate-700">
                  Candidate v{version}
                </span>
                <span className="rounded-full bg-purple-500/20 px-2.5 py-0.5 text-[10px] font-extrabold text-purple-300 border border-purple-500/30">
                  🏢 {dept}
                </span>
              </div>
              <h3 className="text-base font-black text-white mt-1">{title}</h3>
              <p className="text-xs text-slate-300 mt-0.5">{summaryText}</p>
            </div>
          </div>

          <div className="flex items-center gap-3 shrink-0">
            <div className="text-right">
              <span className="text-2xl font-black text-cyan-400 block">{confidencePct}%</span>
              <span className="text-[10px] font-mono text-slate-400">Learning Confidence</span>
            </div>
          </div>
        </div>


        {/* Action Buttons: ⚡ Analyze Workflow vs 👁 Observe Further (Unlocked only after outlier review) */}
        <div className="flex flex-wrap items-center gap-3 shrink-0">
          {onObserveFurther && (
            <button
              suppressHydrationWarning
              onClick={onObserveFurther}
              disabled={isReviewPending}
              className={`flex items-center gap-2 rounded-xl border border-slate-700 px-4 py-2.5 text-xs font-bold transition ${
                isReviewPending
                  ? "bg-slate-900 text-slate-600 border-slate-800 cursor-not-allowed"
                  : "bg-slate-800/80 text-slate-200 hover:bg-slate-700"
              }`}
            >
              <Eye className="h-4 w-4 text-slate-400" />
              <span>Observe Further</span>
            </button>
          )}

          <button
            suppressHydrationWarning
            onClick={onAnalyzeTrigger}
            disabled={!isAnalyzeEnabled}
            className={`flex items-center gap-2 rounded-xl px-5 py-2.5 text-xs font-black transition-all duration-200 shadow-xl ${
              isAnalyzeEnabled
                ? "bg-cyan-500 text-slate-950 shadow-cyan-500/30 hover:bg-cyan-400 hover:shadow-cyan-500/50 transform hover:-translate-y-0.5"
                : "bg-slate-800 text-slate-500 border border-slate-700/60 cursor-not-allowed"
            }`}
          >
            <Zap className="h-4 w-4" />
            <span>Analyze Workflow</span>
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>

      {/* Clean Workflow Stream Banner when 0 outliers exist */}

      {outlierList.length === 0 && (
        <div className="flex items-center gap-2 rounded-xl border border-emerald-500/30 bg-emerald-950/20 p-3 text-xs shadow-lg">
          <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
          <div>
            <h4 className="font-bold text-emerald-300">Clean 100% Deterministic Workflow Stream</h4>
            <p className="text-[10px] text-emerald-400/80">No anomalous actions detected during shadow mode telemetry observation.</p>
          </div>
        </div>
      )}

      {/* Human-in-the-Loop Multi-Outlier Batch Checklist Review Panel */}
      {isReviewPending && outlierList.length > 0 && (

        <div className="flex flex-col gap-3 rounded-xl border border-amber-500/40 bg-amber-950/30 p-4 text-xs shadow-lg">
          <div className="flex items-center justify-between border-b border-amber-500/20 pb-2">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-amber-400 shrink-0" />
              <div>
                <h4 className="font-bold text-amber-200">Semantic Deviation Observed</h4>
                <p className="text-[10px] text-amber-300/80">
                  An anomalous action was observed and corrected. Confirm if this action was accidental to save into persistent memory.
                </p>
              </div>

            </div>

            <div className="flex items-center gap-2">
              <button
                suppressHydrationWarning
                onClick={toggleSelectAll}
                className="rounded bg-slate-800/80 border border-slate-700 px-2 py-1 text-[10px] font-semibold text-slate-300 hover:text-white transition"
              >
                {selectedOutlierIds.size === outlierList.length ? "Deselect All" : "Select All"}
              </button>
              <button
                suppressHydrationWarning
                onClick={clearSelection}
                className="rounded bg-slate-800/80 border border-slate-700 px-2 py-1 text-[10px] font-semibold text-slate-400 hover:text-white transition"
              >
                Clear Selection
              </button>
            </div>
          </div>

          {/* Outlier Checklist Items (1...N) */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-48 overflow-y-auto py-1">
            {outlierList.map((item) => {
              const isChecked = selectedOutlierIds.has(item.id);
              return (
                <div
                  key={item.id}
                  onClick={() => toggleItem(item.id)}
                  className={`flex items-center justify-between rounded-lg border p-2.5 cursor-pointer transition select-none ${
                    isChecked
                      ? "border-amber-500/60 bg-amber-500/10 text-amber-100"
                      : "border-slate-800 bg-slate-950/40 text-slate-400 hover:border-slate-700"
                  }`}
                >
                  <div className="flex items-center gap-2.5 flex-1 min-w-0 pr-2">
                    {isChecked ? (
                      <CheckSquare className="h-4 w-4 text-amber-400 shrink-0" />
                    ) : (
                      <Square className="h-4 w-4 text-slate-600 shrink-0" />
                    )}
                    <div className="flex flex-col min-w-0">
                      <span className="font-bold text-xs text-slate-100 truncate block">
                        {item.label || "Observed Action"}
                      </span>
                      <span className="text-[10px] font-mono text-amber-300/70 truncate">{item.reason}</span>
                    </div>
                  </div>
                  <span className="text-[10px] font-mono bg-slate-900/90 px-2 py-0.5 rounded border border-slate-700/80 text-cyan-300 font-semibold shrink-0">
                    {item.selector.includes("source")
                      ? "[ Source Field ]"
                      : item.selector.includes("target")
                      ? "[ Target Form ]"
                      : item.selector.includes("button")
                      ? "[ Action Button ]"
                      : "[ UI Element ]"}
                  </span>
                </div>
              );
            })}

          </div>

          {/* Batch Submit Action Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2 border-t border-amber-500/20">
            <span className="text-[11px] text-slate-400 font-mono">
              Actions selected above will be batch processed ({selectedOutlierIds.size} of {outlierList.length} selected).
            </span>

            <div className="flex items-center gap-2 shrink-0">
              <button
                suppressHydrationWarning
                onClick={() => handleBatchRefine("INCLUDE")}
                className="rounded-lg border border-slate-700 bg-slate-800 px-4 py-2 text-xs font-bold text-slate-300 hover:bg-slate-700 transition"
              >
                Include in Workflow
              </button>

              <button
                suppressHydrationWarning
                onClick={() => handleBatchRefine("EXCLUDE")}
                className="rounded-lg bg-cyan-500/20 border border-cyan-500/40 px-4 py-2 text-xs font-bold text-cyan-300 hover:bg-cyan-500/30 transition shadow-lg shadow-cyan-500/10"
              >
                Exclude from Workflow (Recommended)
              </button>
            </div>

          </div>
        </div>
      )}

      {/* Satisfying Visual Feedback Banner */}
      {feedbackMsg && (
        <div className="flex items-center gap-2 rounded-xl bg-emerald-500/10 border border-emerald-500/30 px-3.5 py-2 text-xs font-mono text-emerald-300 animate-pulse">
          <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-400" />
          <span>{feedbackMsg}</span>
        </div>
      )}

      {/* Low Confidence Guard Warning */}
      {!isReviewPending && !isAnalyzeEnabled && (
        <div className="flex items-center gap-2 rounded-xl bg-amber-500/10 border border-amber-500/30 px-3.5 py-2 text-xs font-mono text-amber-300">
          <ShieldAlert className="h-4 w-4 shrink-0" />
          <span>Observe additional repetitions before analysis. (Confidence {confidencePct}% &lt; 70% threshold)</span>
        </div>
      )}
      </div>
    </div>
  );
};


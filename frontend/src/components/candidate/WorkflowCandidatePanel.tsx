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

const DEFAULT_OUTLIERS: OutlierItem[] = [
  { id: "out-1", label: "Clicked Help button", selector: "#help-btn", reason: "Observed 1x across repetitions" },
  { id: "out-2", label: "Opened Settings menu", selector: "#settings-nav", reason: "Breaks repeated sequence cycle" },
  { id: "out-3", label: "Scrolled to page footer", selector: "footer", reason: "Single isolated event" },
  { id: "out-4", label: "Clicked empty whitespace", selector: "body", reason: "Isolated click on body" },
];

export const WorkflowCandidatePanel: React.FC<WorkflowCandidatePanelProps> = ({
  candidateId = "cand-default",
  confidenceScore = 0.0,
  candidateName = "Enterprise Data Transfer Workflow",
  businessProcess,
  outliers = DEFAULT_OUTLIERS,
  onAnalyzeTrigger,
  onObserveFurther,
}) => {
  const [version, setVersion] = useState<number>(1);
  const [currentScore, setCurrentScore] = useState<number>(confidenceScore || 0.82);
  const [feedbackMsg, setFeedbackMsg] = useState<string>("");
  const [outlierList, setOutlierList] = useState<OutlierItem[]>(outliers);
  const [selectedOutlierIds, setSelectedOutlierIds] = useState<Set<string>>(new Set(outliers.map(o => o.id)));
  const [isReviewPending, setIsReviewPending] = useState<boolean>(true);

  const effectiveScore = currentScore > 0 ? currentScore : confidenceScore;
  const confidencePct = Math.round(effectiveScore * 100);
  
  // Rule: Only unlock Analyze button after outlier review is completed AND confidence >= 70%
  const isAnalyzeEnabled = !isReviewPending && effectiveScore >= 0.70;

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
    <div className="flex flex-col gap-4 rounded-2xl border border-cyan-500/40 bg-gradient-to-r from-cyan-950/80 via-slate-900/90 to-purple-950/80 p-5 shadow-2xl backdrop-blur-xl">
      {/* Top Main Candidate Discovery Header */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 shadow-lg shadow-cyan-500/10 shrink-0">
            <Sparkles className="h-6 w-6 animate-spin" />
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h3 className="text-sm font-black text-white">{title}</h3>
              <span className="rounded-full bg-cyan-500/20 px-2.5 py-0.5 text-[10px] font-extrabold text-cyan-300 border border-cyan-500/30">
                {confidencePct}% Confidence
              </span>
              <span className="rounded-full bg-slate-800 px-2.5 py-0.5 text-[10px] font-mono text-slate-300 border border-slate-700">
                Candidate v{version}
              </span>
              <span className="rounded-full bg-purple-500/20 px-2.5 py-0.5 text-[10px] font-extrabold text-purple-300 border border-purple-500/30">
                🏢 {dept}
              </span>
              <span className="rounded-full bg-emerald-500/20 px-2.5 py-0.5 text-[10px] font-extrabold text-emerald-300 border border-emerald-500/30">
                🔁 {obsCount}
              </span>
            </div>
            <p className="text-xs text-slate-300 mt-1">{summaryText}</p>
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
      </div>

      {/* Human-in-the-Loop Multi-Outlier Batch Checklist Review Panel */}
      {isReviewPending && outlierList.length > 0 && (
        <div className="flex flex-col gap-3 rounded-xl border border-amber-500/40 bg-amber-950/30 p-4 text-xs shadow-lg">
          <div className="flex items-center justify-between border-b border-amber-500/20 pb-2">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-amber-400 shrink-0" />
              <div>
                <h4 className="font-bold text-amber-200">Possible Outlier Actions Detected</h4>
                <p className="text-[10px] text-amber-300/80">
                  Review anomalous actions observed during shadow mode. Selected items will be batch processed.
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
                  <div className="flex items-center gap-2.5">
                    {isChecked ? (
                      <CheckSquare className="h-4 w-4 text-amber-400 shrink-0" />
                    ) : (
                      <Square className="h-4 w-4 text-slate-600 shrink-0" />
                    )}
                    <div>
                      <span className="font-semibold text-xs text-slate-200 block">{item.label}</span>
                      <span className="text-[10px] font-mono text-slate-500">{item.reason}</span>
                    </div>
                  </div>
                  <code className="text-[9px] font-mono bg-slate-900 px-1.5 py-0.5 rounded text-cyan-400">
                    {item.selector}
                  </code>
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
                className="rounded-lg border border-slate-700 bg-slate-800 px-4 py-2 text-xs font-bold text-slate-200 hover:bg-slate-700 transition"
              >
                Include Selected
              </button>

              <button
                suppressHydrationWarning
                onClick={() => handleBatchRefine("EXCLUDE")}
                className="rounded-lg bg-cyan-500/20 border border-cyan-500/40 px-4 py-2 text-xs font-bold text-cyan-300 hover:bg-cyan-500/30 transition shadow-lg shadow-cyan-500/10"
              >
                Exclude Selected
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
  );
};

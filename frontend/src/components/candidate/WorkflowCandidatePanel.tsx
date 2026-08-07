"use client";

import React, { useState, useEffect } from "react";

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
  observed_destination?: string;
  source_entity?: string;
  expected_destination?: string;
  group?: string;
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
  const [currentScore, setCurrentScore] = useState<number>(confidenceScore);
  const [feedbackMsg, setFeedbackMsg] = useState<string>("");
  const [outlierList, setOutlierList] = useState<OutlierItem[]>(outliers);
  const [selectedOutlierIds, setSelectedOutlierIds] = useState<Set<string>>(new Set(outliers.map(o => o.id)));
  const [isReviewPending, setIsReviewPending] = useState<boolean>(outliers.length > 0);

  const [isCollapsed, setIsCollapsed] = useState<boolean>(false);

  useEffect(() => {
    setOutlierList(outliers);
    setSelectedOutlierIds(new Set(outliers.map(o => o.id)));
    if (outliers && outliers.length > 0) {
      setIsReviewPending(true);
      setIsCollapsed(false);
    } else {
      setIsReviewPending(false);
    }
  }, [outliers]);


  useEffect(() => {
    if (confidenceScore !== undefined) {
      setCurrentScore(confidenceScore);
    }
  }, [confidenceScore]);

  const effectiveScore = currentScore > 0 ? currentScore : confidenceScore;
  const confidencePct = Math.round(effectiveScore * 100);

  // Rule: Enable Analyze button directly when no pending review / 0 active outliers exist
  const isAnalyzeEnabled = (!isReviewPending || outlierList.length === 0);


  const title = businessProcess?.workflow_name || candidateName;
  const dept = businessProcess?.department || "Operations & IT";
  const readiness = businessProcess?.automation_readiness || "High Readiness";
  const obsCount = businessProcess?.repeatability || "3 Observations";
  const summaryText = businessProcess?.summary || "Automates repetitive cross-app data entry workflow.";

  const handleCloseCollapse = () => {
    setIsCollapsed(true);
    if (onObserveFurther) {
      onObserveFurther();
    }
  };

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
    let selectedSelectors = outlierList
      .filter((o) => selectedOutlierIds.has(o.id))
      .map((o) => o.selector || o.observed_destination || o.source_entity || o.id);

    if (selectedSelectors.length === 0 && outlierList.length > 0) {
      selectedSelectors = outlierList.map((o) => o.selector || o.observed_destination || o.source_entity || o.id);
    }

    const targetSel = selectedSelectors.join(",");
    const res = await refineCandidate(candidateId, choice, targetSel);


    const prevPct = Math.round((res?.previous_confidence || effectiveScore) * 100);
    const newPct = Math.round((res?.new_confidence || 0.96) * 100);
    const newVer = res?.version || version + 1;

    setVersion(newVer);
    setCurrentScore(res?.new_confidence || 0.96);
    setOutlierList([]);
    setIsReviewPending(false);

    if (choice === "EXCLUDE") {
      setFeedbackMsg(`✓ Candidate Updated (v${newVer}) — Excluded ${selectedOutlierIds.size} item(s). Confidence: ${prevPct}% → ${newPct}%`);
    } else {
      setFeedbackMsg(`✓ Candidate Updated (v${newVer}) — Included ${selectedOutlierIds.size} item(s). Confidence: ${newPct}%`);
    }
  };

  const handleObserveClick = () => {
    setIsCollapsed(true);
    if (onObserveFurther) {
      onObserveFurther();
    }
  };

  const handleAnalyzeClick = () => {
    setIsCollapsed(true);
    if (onAnalyzeTrigger) {
      onAnalyzeTrigger();
    }
  };



  if (isCollapsed) {
    return (
      <div
        onClick={() => setIsCollapsed(false)}
        className="fixed bottom-6 left-6 z-50 group flex items-center gap-3 cursor-pointer animate-in zoom-in-50 duration-300"
        title="Click to view Discovered Workflow Candidate"
      >
        <div className="relative flex h-14 w-14 items-center justify-center rounded-full border-2 border-cyan-400 bg-gradient-to-br from-cyan-950 via-slate-900 to-purple-950 shadow-2xl shadow-cyan-500/50 hover:scale-110 transition-all duration-300">
          <Sparkles className="h-6 w-6 text-cyan-400 animate-pulse" />
          <span className={`absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full text-[10px] font-black font-mono shadow-md ${
            outlierList.length > 0 ? "bg-amber-400 text-slate-950 animate-bounce" : "bg-cyan-500 text-slate-950"
          }`}>
            {outlierList.length > 0 ? outlierList.length : `v${version}`}
          </span>
        </div>
        <div className="hidden group-hover:flex flex-col rounded-xl border border-cyan-500/40 bg-slate-900/95 px-3 py-1.5 shadow-xl backdrop-blur-md text-xs">
          <span className="font-bold text-cyan-300">{title}</span>
          <span className="text-[10px] text-slate-400 font-mono">
            {outlierList.length > 0 ? `⚠️ ${outlierList.length} mistake(s) detected — Click to review` : `✨ Click to view candidate pattern (${confidencePct}% confidence)`}
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed bottom-6 left-6 z-50 w-full max-w-md animate-in slide-in-from-bottom-8 duration-300">
      <div className="relative flex flex-col gap-4 w-full rounded-2xl border border-cyan-500/50 bg-gradient-to-br from-slate-900/95 via-slate-950/95 to-purple-950/95 p-5 shadow-2xl shadow-cyan-500/25 backdrop-blur-2xl max-h-[calc(100vh-8rem)] overflow-y-auto">

        {/* Dismiss Side Drawer Close Button */}
        <button
          suppressHydrationWarning
          onClick={handleCloseCollapse}
          className="absolute top-3.5 right-3.5 rounded-lg p-1 text-slate-400 hover:bg-slate-800 hover:text-white transition text-xs font-bold"
        >
          ✕
        </button>


        {/* Top Main Candidate Discovery Header */}
        <div className="flex flex-col md:flex-row items-start justify-between gap-4 border-b border-slate-800 pb-4">
          <div className="flex items-center gap-3.5">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 shadow-lg shadow-cyan-500/10 shrink-0">
              <Sparkles className="h-6 w-6 animate-pulse" />
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <span className="rounded-full bg-cyan-500/20 px-2.5 py-0.5 text-[10px] font-mono font-extrabold text-cyan-300 border border-cyan-500/30">
                  🎉 PATTERN RECOGNIZED
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
              onClick={handleObserveClick}

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
            onClick={handleAnalyzeClick}

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
          <div className="flex flex-col gap-2.5 max-h-56 overflow-y-auto py-1">
            {outlierList.map((item) => {
              const isChecked = selectedOutlierIds.has(item.id);
              return (
                <div
                  key={item.id}
                  onClick={() => toggleItem(item.id)}
                  className={`flex items-start justify-between rounded-xl border p-3 cursor-pointer transition select-none ${
                    isChecked
                      ? "border-amber-500/60 bg-amber-500/10 text-amber-100 shadow-md"
                      : "border-slate-800 bg-slate-950/40 text-slate-400 hover:border-slate-700"
                  }`}
                >
                  <div className="flex items-start gap-3 flex-1 min-w-0 pr-2">
                    {isChecked ? (
                      <CheckSquare className="h-4 w-4 text-amber-400 shrink-0 mt-0.5" />
                    ) : (
                      <Square className="h-4 w-4 text-slate-600 shrink-0 mt-0.5" />
                    )}
                    <div className="flex flex-col min-w-0 gap-0.5">
                      <span className="font-bold text-xs text-slate-100 whitespace-normal break-words block leading-snug">
                        {item.label || "Observed Action"}
                      </span>
                      <span className="text-[10px] font-mono text-amber-300/80 whitespace-normal break-words block">
                        {item.reason}
                      </span>
                    </div>
                  </div>
                  <span className="text-[10px] font-mono bg-slate-900/90 px-2 py-1 rounded border border-slate-700/80 text-cyan-300 font-semibold shrink-0">
                    {item.group ? `[ ${item.group} ]` : "[ Semantic Action ]"}
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


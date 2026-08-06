"use client";

import React, { useState } from "react";
import { Sparkles, ArrowRight, Zap, Eye, AlertTriangle, CheckCircle2, ShieldAlert } from "lucide-react";
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

export interface WorkflowCandidatePanelProps {
  candidateId?: string;
  confidenceScore?: number;
  candidateName?: string;
  businessProcess?: BusinessProcessData | null;
  onAnalyzeTrigger: () => void;
  onObserveFurther?: () => void;
}

export const WorkflowCandidatePanel: React.FC<WorkflowCandidatePanelProps> = ({
  candidateId = "cand-default",
  confidenceScore = 0.0,
  candidateName = "Enterprise Data Transfer Workflow",
  businessProcess,
  onAnalyzeTrigger,
  onObserveFurther,
}) => {
  const [version, setVersion] = useState<number>(1);
  const [currentScore, setCurrentScore] = useState<number>(confidenceScore || 0.82);
  const [feedbackMsg, setFeedbackMsg] = useState<string>("");
  const [hasRefinedOutlier, setHasRefinedOutlier] = useState<boolean>(false);
  const [showOutlierCard, setShowOutlierCard] = useState<boolean>(true);

  const effectiveScore = currentScore > 0 ? currentScore : confidenceScore;
  const confidencePct = Math.round(effectiveScore * 100);
  const isAnalyzeEnabled = effectiveScore >= 0.70;

  const title = businessProcess?.workflow_name || candidateName;
  const dept = businessProcess?.department || "Operations & IT";
  const readiness = businessProcess?.automation_readiness || "High Readiness";
  const obsCount = businessProcess?.repeatability || "3 Observations";
  const summaryText = businessProcess?.summary || "Automates repetitive cross-app data entry workflow.";

  const handleRefine = async (choice: "EXCLUDE" | "INCLUDE") => {
    const res = await refineCandidate(candidateId, choice, "#help-btn");
    const prevPct = Math.round((res?.previous_confidence || effectiveScore) * 100);
    const newPct = Math.round((res?.new_confidence || 0.96) * 100);
    const newVer = res?.version || version + 1;

    setVersion(newVer);
    setCurrentScore(res?.new_confidence || 0.96);
    setHasRefinedOutlier(true);

    if (choice === "EXCLUDE") {
      setFeedbackMsg(`✓ Candidate Updated (v${newVer}) — Confidence ${prevPct}% → ${newPct}%`);
    } else {
      setFeedbackMsg(`✓ Step Included in Candidate (v${newVer}) — Confidence ${newPct}%`);
    }
  };

  return (
    <div className="flex flex-col gap-3 rounded-2xl border border-cyan-500/40 bg-gradient-to-r from-cyan-950/80 via-slate-900/90 to-purple-950/80 p-5 shadow-2xl backdrop-blur-xl">
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

        {/* Action Buttons: ⚡ Analyze Workflow vs 👁 Observe Further */}
        <div className="flex flex-wrap items-center gap-3 shrink-0">
          {onObserveFurther && (
            <button
              suppressHydrationWarning
              onClick={onObserveFurther}
              className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-800/80 px-4 py-2.5 text-xs font-bold text-slate-200 hover:bg-slate-700 transition"
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

      {/* Low Confidence Guard Warning */}
      {!isAnalyzeEnabled && (
        <div className="flex items-center gap-2 rounded-xl bg-amber-500/10 border border-amber-500/30 px-3.5 py-2 text-xs font-mono text-amber-300">
          <ShieldAlert className="h-4 w-4 shrink-0" />
          <span>Observe additional repetitions before analysis. (Confidence {confidencePct}% &lt; 70% threshold)</span>
        </div>
      )}

      {/* Satisfying Visual Feedback Banner */}
      {feedbackMsg && (
        <div className="flex items-center gap-2 rounded-xl bg-emerald-500/10 border border-emerald-500/30 px-3.5 py-2 text-xs font-mono text-emerald-300 animate-pulse">
          <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-400" />
          <span>{feedbackMsg}</span>
        </div>
      )}

      {/* Potential Outlier Review Banner */}
      {showOutlierCard && !hasRefinedOutlier && (
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 rounded-xl border border-amber-500/30 bg-amber-950/20 p-3 text-xs">
          <div className="flex items-center gap-2.5">
            <AlertTriangle className="h-4 w-4 text-amber-400 shrink-0" />
            <div>
              <span className="font-bold text-amber-200 block">Potential Outlier Detected</span>
              <span className="text-[11px] text-slate-300">
                Action <code className="bg-slate-900 px-1 py-0.5 rounded text-cyan-300 font-mono">CLICK on #help-btn</code> was observed only 1x across repetitions.
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              suppressHydrationWarning
              onClick={() => handleRefine("INCLUDE")}
              className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-[11px] font-bold text-slate-200 hover:bg-slate-700 transition"
            >
              Include In Workflow
            </button>

            <button
              suppressHydrationWarning
              onClick={() => handleRefine("EXCLUDE")}
              className="rounded-lg bg-cyan-500/20 border border-cyan-500/40 px-3 py-1.5 text-[11px] font-bold text-cyan-300 hover:bg-cyan-500/30 transition shadow-md shadow-cyan-500/10"
            >
              Exclude From Workflow
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

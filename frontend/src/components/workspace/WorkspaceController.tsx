"use client";

import React, { useState } from "react";
import { ProgressStoryBar, WorkspaceStage } from "./ProgressStoryBar";
import { GhostReplay } from "../replay/GhostReplay";
import { WorkflowDNACollapse } from "../dna/WorkflowDNACollapse";
import { AutomationBlueprint } from "../blueprint/AutomationBlueprint";
import { AutomationPipeline } from "../pipeline/AutomationPipeline";
import { HumanApprovalModal } from "../governance/HumanApprovalModal";
import { ObserverDashboard } from "../observer/ObserverDashboard";
import { Brain, ArrowRight, Zap, CheckCircle2 } from "lucide-react";


export interface WorkspaceControllerProps {
  currentStage: WorkspaceStage;
  unlockedStages: WorkspaceStage[];
  confidenceScore: number;
  repetitionCount?: number;
  noiseFilteredCount?: number;
  candidateName?: string;
  onSelectStage: (stage: WorkspaceStage) => void;
  onAnalyzeTrigger: () => void;
  onProceedFromDNA: () => void;
  onProceedFromBlueprint: () => void;
  onPipelineComplete: () => void;
}

export const WorkspaceController: React.FC<WorkspaceControllerProps> = ({
  currentStage,
  unlockedStages,
  confidenceScore,
  repetitionCount = 0,
  noiseFilteredCount = 0,
  candidateName = "Cross-Application Workflow",
  onSelectStage,
  onAnalyzeTrigger,
  onProceedFromDNA,
  onProceedFromBlueprint,
  onPipelineComplete,
}) => {
  const [reconstructionLoading, setReconstructionLoading] = useState<boolean>(false);
  const [showApprovalModal, setShowApprovalModal] = useState<boolean>(false);

  const handleReplayClick = () => {
    setReconstructionLoading(true);
    setTimeout(() => {
      setReconstructionLoading(false);
    }, 1200);
  };

  return (
    <div className="flex flex-col gap-4 w-full h-full">
      {/* Top Tiny Progress Story Bar */}
      <ProgressStoryBar
        currentStage={currentStage}
        unlockedStages={unlockedStages}
        onSelectStage={onSelectStage}
      />

      {/* Dynamic Content Views */}
      <div className="flex-1">
        {currentStage === "OBSERVE" && (
          <div className="flex flex-col items-center justify-center rounded-2xl border border-slate-800 bg-slate-900/80 p-12 text-center h-full">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-xl">
              <span className="text-2xl animate-pulse">👁️</span>
            </div>
            <h3 className="mt-4 text-base font-bold text-slate-100">Continuous Observation Active</h3>
            <p className="mt-1 max-w-md text-xs text-slate-400">
              GhostTrace is quietly observing cross-application interaction patterns in the background.
            </p>
          </div>
        )}

        {currentStage === "ANALYZE" && (
          <div className="flex flex-col gap-6 rounded-2xl border border-slate-800/80 bg-slate-900/90 p-8 shadow-2xl backdrop-blur-xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div>
                <span className="inline-flex items-center gap-1 rounded-md bg-purple-500/10 px-2.5 py-1 text-xs font-bold text-purple-400 border border-purple-500/20">
                  🧠 Pattern Analysis Engine
                </span>
                <h2 className="mt-2 text-lg font-bold text-white">Comparing Repetitions Across Sessions</h2>
                <p className="text-xs text-slate-400">Filtering noise and validating repeated action sequences.</p>
              </div>
              <span className="text-2xl font-black font-mono text-cyan-400">{Math.round(confidenceScore * 100)}%</span>
            </div>

            <div className="grid grid-cols-3 gap-4 text-xs">
              <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
                <span className="text-slate-400 font-semibold">Comparing Repetitions</span>
                <p className="mt-1 font-bold text-cyan-400 font-mono">
                  {repetitionCount > 0 ? `Run #${repetitionCount} sequence matched` : "Waiting for sequence repetitions..."}
                </p>
              </div>
              <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
                <span className="text-slate-400 font-semibold">Noise Filtering</span>
                <p className="mt-1 font-bold text-emerald-400 font-mono">
                  {noiseFilteredCount > 0 ? `${noiseFilteredCount} noise event(s) filtered` : "No noise detected"}
                </p>
              </div>
              <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
                <span className="text-slate-400 font-semibold">Confidence Growth</span>
                <p className="mt-1 font-bold text-purple-400 font-mono">
                  {Math.round(confidenceScore * 100)}% Calculated Score
                </p>
              </div>
            </div>

            {/* High-Impact Decision Banner */}
            <div className="mt-4 flex items-center justify-between rounded-xl border border-cyan-500/40 bg-gradient-to-r from-cyan-950/40 to-purple-950/40 p-5 shadow-xl">
              <div>
                <h4 className="text-sm font-bold text-white">AI detected a repetitive workflow pattern.</h4>
                <p className="text-xs text-slate-300">Target: {candidateName}</p>
              </div>
              <button
                onClick={() => {
                  handleReplayClick();
                  onAnalyzeTrigger();
                }}
                className="flex items-center gap-2 rounded-xl bg-cyan-500 px-5 py-2.5 text-xs font-bold text-slate-950 shadow-lg shadow-cyan-500/30 hover:bg-cyan-400 transition-all"
              >
                <span>Analyze & Build Automation</span>
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}

        {currentStage === "DNA" && (
          <WorkflowDNACollapse onProceed={onProceedFromDNA} />
        )}

        {currentStage === "BLUEPRINT" && (
          <AutomationBlueprint onProceedToDeploy={onProceedFromBlueprint} />
        )}

        {currentStage === "REPLAY" && (
          <div>
            {reconstructionLoading ? (
              <div className="flex flex-col items-center justify-center rounded-2xl border border-slate-800 bg-slate-900/90 p-12 text-center">
                <div className="h-10 w-10 animate-spin rounded-full border-4 border-cyan-500 border-t-transparent" />
                <h4 className="mt-4 text-sm font-bold text-slate-200">Preparing Visual Reconstruction...</h4>
                <p className="text-xs text-slate-400">Synthesizing 60fps ghost cursor path from telemetry</p>
              </div>
            ) : (
              <GhostReplay onProceedToDeploy={() => setShowApprovalModal(true)} />
            )}
          </div>
        )}

        {showApprovalModal && (
          <HumanApprovalModal
            onApprove={() => {
              setShowApprovalModal(false);
              onProceedFromBlueprint();
            }}
            onReject={() => setShowApprovalModal(false)}
          />
        )}


        {currentStage === "DEPLOY" && (
          <AutomationPipeline onCompletePipeline={onPipelineComplete} />
        )}

        {currentStage === "OPERATIONS" && (
          <div className="flex flex-col gap-6">
            <ObserverDashboard />
          </div>
        )}

      </div>
    </div>
  );
};

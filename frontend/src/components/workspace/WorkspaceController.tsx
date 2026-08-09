"use client";

import React, { useState } from "react";
import { ProgressStoryBar, WorkspaceStage } from "./ProgressStoryBar";
import { GhostReplay } from "../replay/GhostReplay";
import { WorkflowDNACollapse } from "../dna/WorkflowDNACollapse";
import { AutomationBlueprint } from "../blueprint/AutomationBlueprint";
import { AutomationPipeline } from "../pipeline/AutomationPipeline";
import { HumanApprovalModal } from "../governance/HumanApprovalModal";
import { ObserverDashboard } from "../observer/ObserverDashboard";
import { ShadowModePanel } from "../command-center/ShadowModePanel";
import { ReasoningDashboard } from "../reasoning/ReasoningDashboard";
import { ObservationSnapshot } from "../command-center/CommandCenterDashboard";

export interface WorkspaceControllerProps {
  currentStage: WorkspaceStage;
  unlockedStages: WorkspaceStage[];
  confidenceScore: number;
  repetitionCount?: number;
  noiseFilteredCount?: number;
  candidateName?: string;
  workflowDNA?: any;
  fieldMappings?: any[];
  chronologicalTransfers?: any[];
  outliers?: any[];
  observationSessionId?: string;
  lockedSnapshot?: ObservationSnapshot | null;
  onSelectStage: (stage: WorkspaceStage) => void;
  onAnalyzeTrigger: () => void;
  onProceedToDNAFromAnalyze?: () => void;
  onProceedFromDNA: () => void;
  onProceedFromBlueprint: () => void;
  onPipelineComplete: () => void;
  onResetShadowMode?: () => void;
}

export const WorkspaceController: React.FC<WorkspaceControllerProps> = ({
  currentStage,
  unlockedStages,
  confidenceScore,
  repetitionCount = 0,
  noiseFilteredCount = 0,
  candidateName = "Cross-Application Workflow",
  workflowDNA,
  fieldMappings = [],
  chronologicalTransfers = [],
  outliers = [],
  observationSessionId = "",
  lockedSnapshot = null,
  onSelectStage,
  onAnalyzeTrigger,
  onProceedToDNAFromAnalyze,
  onProceedFromDNA,
  onProceedFromBlueprint,
  onPipelineComplete,
  onResetShadowMode,
}) => {
  const [reconstructionLoading, setReconstructionLoading] = useState<boolean>(false);
  const [showApprovalModal, setShowApprovalModal] = useState<boolean>(false);

  // Read effective downstream snapshot fields
  const effectiveConfidence = lockedSnapshot?.confidenceScore !== undefined ? lockedSnapshot.confidenceScore : confidenceScore;
  const effectiveRepetition = lockedSnapshot?.repetitionCount !== undefined ? lockedSnapshot.repetitionCount : repetitionCount;
  const effectiveNoise = lockedSnapshot?.noiseFilteredCount !== undefined ? lockedSnapshot.noiseFilteredCount : noiseFilteredCount;
  const effectiveName = lockedSnapshot?.candidateName || candidateName;
  const effectiveDNA = lockedSnapshot?.workflowDNA || workflowDNA;
  const effectiveMappings = lockedSnapshot?.fieldMappings?.length ? lockedSnapshot.fieldMappings : fieldMappings;
  const effectiveTransfers = lockedSnapshot?.chronologicalTransfers?.length ? lockedSnapshot.chronologicalTransfers : chronologicalTransfers;
  const effectiveOutliers = lockedSnapshot?.outliers ? lockedSnapshot.outliers : outliers;
  const effectiveSessionId = lockedSnapshot?.sessionId || observationSessionId;
  const effectiveSynthesis = lockedSnapshot?.observationSynthesis || null;

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
          <ShadowModePanel
            repetitionCount={repetitionCount}
            confidenceScore={confidenceScore}
            onReset={onResetShadowMode}
          />
        )}

        {currentStage === "ANALYZE" && (
          <ReasoningDashboard
            confidenceScore={effectiveConfidence}
            repetitionCount={effectiveRepetition}
            noiseFilteredCount={effectiveNoise}
            candidateName={effectiveName}
            workflowDNA={effectiveDNA}
            fieldMappings={effectiveMappings}
            chronologicalTransfers={effectiveTransfers}
            outliers={effectiveOutliers}
            observationSessionId={effectiveSessionId}
            observationSynthesis={effectiveSynthesis}
            onProceedToDNA={onProceedToDNAFromAnalyze || onAnalyzeTrigger}
            onObserveFurther={() => onSelectStage("OBSERVE")}
          />
        )}

        {currentStage === "DNA" && (
          <WorkflowDNACollapse
            workflowDNA={effectiveDNA}
            fieldMappings={effectiveMappings}
            chronologicalTransfers={effectiveTransfers}
            observationSessionId={effectiveSessionId}
            repetitionCount={effectiveRepetition}
            observationSynthesis={effectiveSynthesis}
            onProceed={onProceedFromDNA}
          />
        )}

        {currentStage === "BLUEPRINT" && (
          <AutomationBlueprint
            workflowDNA={effectiveDNA}
            observationSynthesis={effectiveSynthesis}
            onProceedToDeploy={onProceedFromBlueprint}
          />
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
              <GhostReplay
                workflowDNA={effectiveDNA}
                observationSynthesis={effectiveSynthesis}
                onProceedToDeploy={() => setShowApprovalModal(true)}
              />
            )}
          </div>
        )}

        {showApprovalModal && (
          <HumanApprovalModal
            onApprove={() => {
              setShowApprovalModal(false);
              onSelectStage("DEPLOY");
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

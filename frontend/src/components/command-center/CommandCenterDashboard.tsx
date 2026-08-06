"use client";

import React, { useState, useEffect } from "react";
import { AppAccessPermission } from "../onboarding/AppAccessPermission";
import { CommandCenterHeader } from "./CommandCenterHeader";
import { ShadowModePanel } from "./ShadowModePanel";
import { AIWorkforce } from "../workforce/AIWorkforce";
import { WorkspaceController } from "../workspace/WorkspaceController";
import { WorkspaceStage } from "../workspace/ProgressStoryBar";
import { WorkflowCandidatePanel } from "../candidate/WorkflowCandidatePanel";
import { ReasoningTimeline } from "../reasoning/ReasoningTimeline";
import { DigitalEmployeeCard } from "../employee/DigitalEmployeeCard";
import { AutomationImpactCard } from "../impact/AutomationImpactCard";
import { fetchGraphState, triggerGraphExecution } from "@/lib/api";

export const CommandCenterDashboard: React.FC = () => {
  const [showPermissionModal, setShowPermissionModal] = useState<boolean>(false);
  const [monitoredApps, setMonitoredApps] = useState<string[]>(["Chrome", "SAP ERP", "Excel"]);
  const [currentStage, setCurrentStage] = useState<WorkspaceStage>("OBSERVE");
  const [unlockedStages, setUnlockedStages] = useState<WorkspaceStage[]>(["OBSERVE", "ANALYZE"]);
  const [confidenceScore, setConfidenceScore] = useState<number>(0.0);
  const [repetitionCount, setRepetitionCount] = useState<number>(0);
  const [noiseFilteredCount, setNoiseFilteredCount] = useState<number>(0);
  const [candidateName, setCandidateName] = useState<string>("Waiting for interaction events...");

  const handleResetShadowMode = () => {
    setCurrentStage("OBSERVE");
    setConfidenceScore(0.0);
    setRepetitionCount(0);
    setNoiseFilteredCount(0);
    setCandidateName("Waiting for interaction events...");
  };

  useEffect(() => {
    // Poll graph state from backend
    const interval = setInterval(() => {
      fetchGraphState().then((state) => {
        if (state) {
          if (state.confidence_score !== undefined) setConfidenceScore(state.confidence_score);
          if (state.repetition_count !== undefined) setRepetitionCount(state.repetition_count);
          if (state.noise_filtered_count !== undefined) setNoiseFilteredCount(state.noise_filtered_count);
          if (state.candidate_name) setCandidateName(state.candidate_name);
        }
      });
    }, 1000);

    return () => clearInterval(interval);
  }, []);


  const handleGrantPermission = (selectedApps: string[]) => {
    setMonitoredApps(selectedApps);
    setShowPermissionModal(false);
  };

  const handleAnalyzeTrigger = () => {
    setUnlockedStages(["OBSERVE", "ANALYZE", "REPLAY", "DNA"]);
    setCurrentStage("REPLAY");
    triggerGraphExecution({ action: "ANALYZE" });
  };

  const handleProceedFromDNA = () => {
    setUnlockedStages(["OBSERVE", "ANALYZE", "REPLAY", "DNA", "BLUEPRINT"]);
    setCurrentStage("BLUEPRINT");
  };

  const handleProceedFromBlueprint = () => {
    setUnlockedStages(["OBSERVE", "ANALYZE", "REPLAY", "DNA", "BLUEPRINT", "DEPLOY"]);
    setCurrentStage("DEPLOY");
  };

  const handlePipelineComplete = () => {
    setUnlockedStages(["OBSERVE", "ANALYZE", "REPLAY", "DNA", "BLUEPRINT", "DEPLOY", "OPERATIONS"]);
    setCurrentStage("OPERATIONS");
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans p-4 md:p-6 flex flex-col gap-6 selection:bg-cyan-500 selection:text-slate-950">
      {/* Onboarding Permission Modal */}
      {showPermissionModal && <AppAccessPermission onGrantPermission={handleGrantPermission} />}

      {/* Top Enterprise Header */}
      <CommandCenterHeader
        shadowModeActive={!showPermissionModal}
        monitoredApps={monitoredApps}
        confidenceScore={confidenceScore}
      />

      {/* Main 3-Column Enterprise Operating System Layout */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12 flex-1">
        {/* Left Column (3 cols): AI WORKFORCE (WHO is thinking) */}
        <div className="lg:col-span-3 flex flex-col gap-6">
          <AIWorkforce currentStage={currentStage} />
          <ShadowModePanel
            repetitionCount={repetitionCount}
            confidenceScore={confidenceScore}
            onReset={handleResetShadowMode}
          />

        </div>

        {/* Center Column (6 cols): MAIN WORKSPACE (WHAT you're looking at) */}
        <div className="lg:col-span-6 flex flex-col gap-6">
          <WorkspaceController
            currentStage={currentStage}
            unlockedStages={unlockedStages}
            confidenceScore={confidenceScore}
            repetitionCount={repetitionCount}
            noiseFilteredCount={noiseFilteredCount}
            candidateName={candidateName}
            onSelectStage={setCurrentStage}
            onAnalyzeTrigger={handleAnalyzeTrigger}
            onProceedFromDNA={handleProceedFromDNA}
            onProceedFromBlueprint={handleProceedFromBlueprint}
            onPipelineComplete={handlePipelineComplete}
          />
        </div>

        {/* Right Column (3 cols): REASONING TIMELINE (WHY it happened) */}
        <div className="lg:col-span-3 flex flex-col gap-6">
          <ReasoningTimeline />
        </div>
      </div>

      {/* Bottom Bar: Candidate Discovery Panel OR Digital Employee Status & ROI */}
      <div className="flex flex-col gap-4">
        {currentStage === "ANALYZE" && (
          <WorkflowCandidatePanel
            confidenceScore={confidenceScore}
            candidateName={candidateName}
            onAnalyzeTrigger={handleAnalyzeTrigger}
          />
        )}

        {currentStage === "OPERATIONS" && (
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <DigitalEmployeeCard isDeploying={false} />
            <AutomationImpactCard />
          </div>
        )}
      </div>
    </div>
  );
};

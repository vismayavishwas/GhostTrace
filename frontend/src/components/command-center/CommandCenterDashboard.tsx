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
import { fetchGraphState, triggerGraphExecution, resetTelemetryState } from "@/lib/api";


import { InteractiveSandboxApp } from "../sandbox/InteractiveSandboxApp";

export const CommandCenterDashboard: React.FC = () => {
  const [showPermissionModal, setShowPermissionModal] = useState<boolean>(false);
  const [monitoredApps, setMonitoredApps] = useState<string[]>(["Chrome", "SAP ERP", "Excel"]);
  const [currentStage, setCurrentStage] = useState<WorkspaceStage>("OBSERVE");
  const [unlockedStages, setUnlockedStages] = useState<WorkspaceStage[]>(["OBSERVE", "ANALYZE"]);
  const [confidenceScore, setConfidenceScore] = useState<number>(0.0);
  const [repetitionCount, setRepetitionCount] = useState<number>(0);
  const [noiseFilteredCount, setNoiseFilteredCount] = useState<number>(0);
  const [candidateName, setCandidateName] = useState<string>("Waiting for interaction events...");
  const [businessProcess, setBusinessProcess] = useState<any>(null);
  const [outliers, setOutliers] = useState<any[]>([]);
  const [candidateDismissed, setCandidateDismissed] = useState<boolean>(false);
  const [workflowDNA, setWorkflowDNA] = useState<any>(null);

  useEffect(() => {
    // Poll graph state from backend
    const interval = setInterval(() => {
      fetchGraphState().then((state) => {
        if (state) {

          if (state.confidence_score !== undefined) setConfidenceScore(state.confidence_score);
          if (state.repetition_count !== undefined) setRepetitionCount(state.repetition_count);
          if (state.noise_filtered_count !== undefined) setNoiseFilteredCount(state.noise_filtered_count);
          if (state.candidate_name) setCandidateName(state.candidate_name);
          if (state.business_process) setBusinessProcess(state.business_process);
          if (state.outliers) setOutliers(state.outliers);
          if (state.workflow_dna) setWorkflowDNA(state.workflow_dna);

          // Milestone 3: Unlock ANALYZE stage when pattern is detected (repetition >= 2 or confidence >= 0.70)
          if ((state.repetition_count && state.repetition_count >= 2) || (state.confidence_score && state.confidence_score >= 0.70)) {
            setUnlockedStages((prev) => (prev.includes("ANALYZE") ? prev : [...prev, "ANALYZE"]));
          }
        }
      });
    }, 500);


    return () => clearInterval(interval);
  }, []);

  const handleGrantPermission = (selectedApps: string[]) => {
    setMonitoredApps(selectedApps);
    setShowPermissionModal(false);
  };

  const handleAnalyzeTrigger = async () => {
    setCandidateDismissed(true);
    setUnlockedStages(["OBSERVE", "ANALYZE", "DNA"]);
    setCurrentStage("DNA");
    const res = await triggerGraphExecution({ action: "ANALYZE" });
    if (res?.state?.workflow_dna) {
      setWorkflowDNA(res.state.workflow_dna);
    }
  };

  const handleProceedFromDNA = () => {
    setUnlockedStages(["OBSERVE", "ANALYZE", "DNA", "BLUEPRINT"]);
    setCurrentStage("BLUEPRINT");
  };

  const handleProceedFromBlueprint = () => {
    setUnlockedStages(["OBSERVE", "ANALYZE", "DNA", "BLUEPRINT", "REPLAY"]);
    setCurrentStage("REPLAY");
  };

  const handleProceedFromReplay = () => {
    setUnlockedStages(["OBSERVE", "ANALYZE", "DNA", "BLUEPRINT", "REPLAY", "DEPLOY"]);
    setCurrentStage("DEPLOY");
  };

  const handlePipelineComplete = () => {
    setUnlockedStages(["OBSERVE", "ANALYZE", "DNA", "BLUEPRINT", "REPLAY", "DEPLOY", "OPERATIONS"]);
    setCurrentStage("OPERATIONS");
  };


  const handleResetShadowMode = () => {
    resetTelemetryState();
    setConfidenceScore(0.0);
    setRepetitionCount(0);
    setNoiseFilteredCount(0);
    setCandidateName("Waiting for interaction events...");
    setBusinessProcess(null);
    setOutliers([]);
    setWorkflowDNA(null);
    setCandidateDismissed(false);
    setUnlockedStages(["OBSERVE"]);
    setCurrentStage("OBSERVE");

    if (typeof window !== "undefined") {
      window.dispatchEvent(new CustomEvent("ghosttrace:reset-sandbox"));
    }
  };


  const handleObserveFurther = () => {
    setCurrentStage("OBSERVE");
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

      {/* Live Interactive Sandboxed Enterprise Demo Web App */}
      {(currentStage === "OBSERVE" || currentStage === "OPERATIONS") && <InteractiveSandboxApp />}


      {/* Main 3-Column Enterprise Operating System Layout */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12 flex-1">

        {/* Left Column (3 cols): AI WORKFORCE (WHO is thinking) */}
        <div className="lg:col-span-3 flex flex-col gap-6">
          <AIWorkforce currentStage={currentStage} />
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
            workflowDNA={workflowDNA}
            onSelectStage={setCurrentStage}
            onAnalyzeTrigger={handleAnalyzeTrigger}
            onProceedFromDNA={handleProceedFromDNA}
            onProceedFromBlueprint={handleProceedFromBlueprint}
            onPipelineComplete={handlePipelineComplete}
            onResetShadowMode={handleResetShadowMode}
          />
        </div>


        {/* Right Column (3 cols): REASONING TIMELINE (WHY it happened) */}
        <div className="lg:col-span-3 flex flex-col gap-6">
          <ReasoningTimeline
            currentStage={currentStage}
            confidenceScore={confidenceScore}
            repetitionCount={repetitionCount}
            noiseFilteredCount={noiseFilteredCount}
            candidateName={candidateName}
            businessProcess={businessProcess}
          />
        </div>

      </div>


      {/* Bottom Bar: Candidate Discovery Panel (Unlocked on pattern repetition >= 1 or active HITL outliers) */}
      <div className="flex flex-col gap-4">
        {(repetitionCount >= 1 || (outliers && outliers.length > 0)) && (
          <WorkflowCandidatePanel
            confidenceScore={confidenceScore}
            candidateName={candidateName !== "Waiting for interaction events..." ? candidateName : "Discovered Cross-App Workflow"}
            businessProcess={businessProcess}
            outliers={outliers}
            onAnalyzeTrigger={handleAnalyzeTrigger}
            onObserveFurther={handleObserveFurther}
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

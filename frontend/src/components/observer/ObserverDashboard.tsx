"use client";

import React, { useState } from "react";
import { WorkflowCandidates, CandidateData } from "./WorkflowCandidates";
import { NotificationsPanel, NotificationData } from "./NotificationsPanel";

export interface ObserverDashboardProps {
  candidates?: CandidateData[];
  notifications?: NotificationData[];
  telemetryCount?: number;
  onCandidateSelect?: (candidate: CandidateData) => void;
}

export const ObserverDashboard: React.FC<ObserverDashboardProps> = ({
  candidates = [],
  notifications = [],
  telemetryCount = 0,
  onCandidateSelect,
}) => {

  return (
    <div className="flex flex-col gap-6 w-full max-w-7xl mx-auto p-6">
      {/* Top Banner & Stats Overview */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 rounded-2xl border border-slate-800 bg-slate-900/90 p-6 shadow-2xl backdrop-blur-md">
        <div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center rounded-md bg-cyan-500/10 px-2 py-1 text-xs font-medium text-cyan-400 border border-cyan-500/20">
              Phase 12
            </span>
            <h1 className="text-xl font-extrabold tracking-tight text-white">Continuous Observer Dashboard</h1>
          </div>
          <p className="mt-1 text-xs text-slate-400">
            Passive background perception monitoring post-deployment telemetry stream & discovering workflow patterns.
          </p>
        </div>

        {/* Stats Grid */}
        <div className="flex items-center gap-6">
          <div className="flex flex-col">
            <span className="text-[11px] font-medium text-slate-500">Telemetry Ingested</span>
            <span className="text-lg font-bold font-mono text-cyan-400">{telemetryCount.toLocaleString()}</span>
          </div>
          <div className="h-8 w-[1px] bg-slate-800" />
          <div className="flex flex-col">
            <span className="text-[11px] font-medium text-slate-500">Discovered Flows</span>
            <span className="text-lg font-bold font-mono text-purple-400">{candidates.length}</span>
          </div>
          <div className="h-8 w-[1px] bg-slate-800" />
          <div className="flex flex-col">
            <span className="text-[11px] font-medium text-slate-500">Observer Status</span>
            <span className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-400">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              READ-ONLY
            </span>
          </div>
        </div>
      </div>

      {/* Main Grid: Left Candidates View, Right Notifications Stream */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <WorkflowCandidates candidates={candidates} onSelectCandidate={onCandidateSelect} />
        </div>
        <div className="lg:col-span-1">
          <NotificationsPanel notifications={notifications} />
        </div>
      </div>
    </div>
  );
};

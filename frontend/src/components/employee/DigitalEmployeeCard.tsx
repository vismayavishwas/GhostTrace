"use client";

import React, { useState, useEffect } from "react";
import { Bot, CheckCircle2, Zap, Activity, Clock, ShieldCheck } from "lucide-react";

export interface DigitalEmployeeCardProps {
  isDeploying?: boolean;
}

export const DigitalEmployeeCard: React.FC<DigitalEmployeeCardProps> = ({ isDeploying = false }) => {
  const [deployStep, setDeployStep] = useState<number>(isDeploying ? 0 : 4);

  useEffect(() => {
    if (!isDeploying) {
      setDeployStep(4);
      return;
    }

    const steps = [
      "Deploying Agent...",
      "Registering Worker...",
      "Synchronizing Memory...",
      "Watching Inbox...",
      "READY",
    ];

    let current = 0;
    const interval = setInterval(() => {
      current += 1;
      setDeployStep(current);
      if (current >= steps.length - 1) {
        clearInterval(interval);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [isDeploying]);

  const deployMessages = [
    "Deploying Agent...",
    "Registering Worker...",
    "Synchronizing Memory...",
    "Watching Inbox...",
    "✓ Digital Employee Active",
  ];

  return (
    <div className="flex flex-col md:flex-row items-center justify-between gap-4 rounded-2xl border border-slate-800/80 bg-slate-900/90 p-5 shadow-xl backdrop-blur-xl">
      <div className="flex items-center gap-3.5">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-500/20 to-emerald-500/20 text-emerald-400 border border-emerald-500/30 shadow-md">
          <Bot className="h-6 w-6" />
        </div>

        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-black text-white">Invoice Processor #001</h3>
            <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 px-2 py-0.5 text-[10px] font-bold text-emerald-400 border border-emerald-500/20">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
              {deployMessages[Math.min(deployStep, 4)]}
            </span>
          </div>
          <p className="text-xs text-slate-400">Deployed Digital Employee • Autonomous Background Worker</p>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
        <div className="flex flex-col">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Next Trigger</span>
          <span className="font-bold text-slate-200">New Gmail Invoice</span>
        </div>

        <div className="flex flex-col">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Jobs Completed</span>
          <span className="font-bold font-mono text-cyan-400">18 runs</span>
        </div>

        <div className="flex flex-col">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Avg Runtime</span>
          <span className="font-bold font-mono text-purple-400">182ms</span>
        </div>

        <div className="flex flex-col">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Health Index</span>
          <span className="font-bold font-mono text-emerald-400">98% Optimal</span>
        </div>
      </div>
    </div>
  );
};

"use client";

import React from "react";
import { Eye, Brain, Dna, Code2, TestTube, Wrench, Rocket, Cpu } from "lucide-react";
import { WorkspaceStage } from "../workspace/ProgressStoryBar";

export interface AIWorker {
  id: string;
  name: string;
  role: string;
  status: "Watching 👁️" | "Learning 🧠" | "Modeling 🧬" | "Building ⚙️" | "Testing 🧪" | "Sleeping 😴" | "Active 🚀" | "Idle 💤";
  isActive: boolean;
  icon: any;
}

export interface AIWorkforceProps {
  currentStage: WorkspaceStage;
}

export const AIWorkforce: React.FC<AIWorkforceProps> = ({ currentStage }) => {
  const getWorkers = (stage: WorkspaceStage): AIWorker[] => {
    return [
      {
        id: "worker-observer",
        name: "Observer Agent",
        role: "Telemetry perception stream",
        status: stage === "OBSERVE" ? "Watching 👁️" : "Idle 💤",
        isActive: stage === "OBSERVE",
        icon: Eye,
      },
      {
        id: "worker-pattern",
        name: "Pattern Analyst",
        role: "Sequence clustering engine",
        status: stage === "ANALYZE" ? "Learning 🧠" : "Idle 💤",
        isActive: stage === "ANALYZE",
        icon: Brain,
      },
      {
        id: "worker-dna",
        name: "DNA Architect",
        role: "Semantic step extraction",
        status: stage === "DNA" || stage === "BLUEPRINT" ? "Modeling 🧬" : "Idle 💤",
        isActive: stage === "DNA" || stage === "BLUEPRINT",
        icon: Dna,
      },
      {
        id: "worker-compiler",
        name: "Playwright Compiler",
        role: "Python script synthesis",
        status: stage === "DEPLOY" ? "Building ⚙️" : "Idle 💤",
        isActive: stage === "DEPLOY",
        icon: Code2,
      },
      {
        id: "worker-sandbox",
        name: "Sandbox Tester",
        role: "Subprocess verification",
        status: stage === "DEPLOY" ? "Testing 🧪" : "Idle 💤",
        isActive: stage === "DEPLOY",
        icon: TestTube,
      },
      {
        id: "worker-recovery",
        name: "Recovery Engineer",
        role: "Self-healing repair engine",
        status: "Sleeping 😴",
        isActive: false,
        icon: Wrench,
      },
      {
        id: "worker-automation",
        name: "Automation Driver",
        role: "Autonomous digital employee",
        status: stage === "OPERATIONS" ? "Active 🚀" : "Idle 💤",
        isActive: stage === "OPERATIONS",
        icon: Rocket,
      },
    ];
  };

  const workers = getWorkers(currentStage);

  return (
    <div className="flex flex-col gap-4 rounded-2xl border border-slate-800/80 bg-slate-900/80 p-5 shadow-xl backdrop-blur-xl h-full">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <div className="flex items-center gap-2">
          <div className="rounded-lg bg-cyan-500/10 p-2 text-cyan-400 border border-cyan-500/20">
            <Cpu className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100">AI Workforce Roster</h3>
            <p className="text-[10px] text-slate-400">Live agent worker personalities</p>
          </div>
        </div>
        <span className="text-[10px] font-mono text-slate-500">{workers.filter(w => w.isActive).length} active</span>
      </div>

      <div className="flex flex-col gap-2 max-h-[460px] overflow-y-auto pr-1">
        {workers.map((worker) => {
          const Icon = worker.icon;
          return (
            <div
              key={worker.id}
              className={`flex items-center justify-between rounded-xl border p-3 transition duration-200 ${
                worker.isActive
                  ? "border-cyan-500/50 bg-cyan-950/20 shadow-md shadow-cyan-500/5"
                  : "border-slate-800/50 bg-slate-950/40 opacity-70"
              }`}
            >
              <div className="flex items-center gap-3">
                <div
                  className={`rounded-lg p-2 ${
                    worker.isActive ? "bg-cyan-500/20 text-cyan-400" : "bg-slate-800 text-slate-400"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-200">{worker.name}</h4>
                  <p className="text-[10px] text-slate-400">{worker.role}</p>
                </div>
              </div>

              <span
                className={`rounded-full px-2.5 py-1 text-[10px] font-bold ${
                  worker.isActive
                    ? "bg-cyan-500/10 text-cyan-300 border border-cyan-500/20"
                    : "bg-slate-800/60 text-slate-500"
                }`}
              >
                {worker.status}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

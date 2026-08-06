"use client";

import React, { useState, useEffect } from "react";
import { Code2, TestTube, Wrench, Rocket, CheckCircle2, AlertTriangle, WifiOff } from "lucide-react";
import { WebSocketStreamManager } from "@/lib/websocket";

export interface AutomationPipelineProps {
  onCompletePipeline?: () => void;
}

export const AutomationPipeline: React.FC<AutomationPipelineProps> = ({ onCompletePipeline }) => {
  const [stageIndex, setStageIndex] = useState<number>(0);
  const [isSelfHealing, setIsSelfHealing] = useState<boolean>(false);
  const [isConnected, setIsConnected] = useState<boolean>(false);

  const stages = [
    { id: "code_gen", name: "Code Generation", detail: "Synthesizing modular Playwright Python script...", icon: Code2 },
    { id: "sandbox", name: "Sandbox Testing", detail: "Isolated subprocess execution check...", icon: TestTube },
    { id: "self_heal", name: "Self-Healing Repair", detail: "LLM diagnosis & v2 version patch...", icon: Wrench },
    { id: "deploy", name: "Agent Deployment", detail: "Registering Digital Employee...", icon: Rocket },
  ];

  useEffect(() => {
    const wsManager = new WebSocketStreamManager(
      "pipeline",
      (msg) => {
        if (msg && msg.payload) {
          const payload = msg.payload;
          if (payload.stage_index !== undefined) {
            setStageIndex(payload.stage_index);
          }
          if (payload.is_self_healing !== undefined) {
            setIsSelfHealing(payload.is_self_healing);
          }
          if (payload.completed && onCompletePipeline) {
            onCompletePipeline();
          }
        }
      },
      (connected) => setIsConnected(connected)
    );

    return () => wsManager.close();
  }, [onCompletePipeline]);

  return (
    <div className="flex flex-col gap-6 rounded-2xl border border-slate-800/80 bg-slate-900/90 p-6 shadow-2xl backdrop-blur-xl">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
        <div>
          <span className="inline-flex items-center gap-1.5 rounded-md bg-cyan-500/10 px-2.5 py-1 text-xs font-bold text-cyan-400 border border-cyan-500/20">
            ⚙️ Compiler & Deployment Engine
          </span>
          <h2 className="mt-2 text-lg font-bold text-white">Automation Pipeline Execution</h2>
          <p className="text-xs text-slate-400">Compiling Workflow DNA into executable Playwright Python code with sandbox isolation.</p>
        </div>

        {!isConnected && (
          <span className="inline-flex items-center gap-1 rounded-xl border border-amber-500/30 bg-amber-500/10 px-3 py-1.5 text-xs font-bold text-amber-400">
            <WifiOff className="h-3.5 w-3.5" />
            Waiting for backend pipeline...
          </span>
        )}
      </div>

      {/* Pipeline Stage Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {stages.map((stg, idx) => {
          const Icon = stg.icon;
          const isDone = idx < stageIndex;
          const isCurrent = idx === stageIndex;

          return (
            <div
              key={stg.id}
              className={`flex flex-col justify-between rounded-xl border p-4 transition-all duration-300 ${
                isCurrent
                  ? isSelfHealing
                    ? "border-amber-500/60 bg-amber-950/20 shadow-lg shadow-amber-500/10"
                    : "border-cyan-500/60 bg-cyan-950/20 shadow-lg shadow-cyan-500/10"
                  : isDone
                  ? "border-emerald-500/30 bg-slate-950/80"
                  : "border-slate-800/50 bg-slate-950/30 opacity-50"
              }`}
            >
              <div className="flex items-center justify-between">
                <div className={`rounded-lg p-2.5 ${isCurrent ? "bg-cyan-500/20 text-cyan-400" : isDone ? "bg-emerald-500/20 text-emerald-400" : "bg-slate-800 text-slate-500"}`}>
                  <Icon className="h-5 w-5" />
                </div>
                {isDone && <CheckCircle2 className="h-5 w-5 text-emerald-400" />}
                {isCurrent && <span className="h-2 w-2 rounded-full bg-cyan-400 animate-ping" />}
              </div>

              <div className="mt-4">
                <h4 className="text-xs font-bold text-slate-100">{stg.name}</h4>
                <p className="mt-1 text-[11px] text-slate-400">{stg.detail}</p>
              </div>

              <div className="mt-3 pt-2 border-t border-slate-800/50 flex items-center justify-between text-[10px]">
                <span className="font-mono text-slate-500">STAGE {idx + 1}</span>
                <span className={`font-bold ${isDone ? "text-emerald-400" : isCurrent ? "text-cyan-400" : "text-slate-600"}`}>
                  {isDone ? "DONE" : isCurrent ? "RUNNING" : "WAITING"}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {isSelfHealing && (
        <div className="rounded-xl border border-amber-500/40 bg-amber-950/30 p-4 text-xs text-amber-300 flex items-center justify-between animate-pulse">
          <div className="flex items-center gap-2">
            <Wrench className="h-4 w-4 text-amber-400" />
            <span>Self-Healing Triggered: Diagnosed selector failure on line 12. Synthesizing versioned patch v2...</span>
          </div>
          <span className="font-bold font-mono">AUTOREPAIR IN PROGRESS</span>
        </div>
      )}
    </div>
  );
};

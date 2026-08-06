"use client";

import React from "react";
import { Check, Lock } from "lucide-react";

export type WorkspaceStage = "OBSERVE" | "ANALYZE" | "REPLAY" | "DNA" | "BLUEPRINT" | "DEPLOY" | "OPERATIONS";

export interface ProgressStoryBarProps {
  currentStage: WorkspaceStage;
  unlockedStages: WorkspaceStage[];
  onSelectStage: (stage: WorkspaceStage) => void;
}

const STAGES: { id: WorkspaceStage; label: string; icon: string }[] = [
  { id: "OBSERVE", label: "Observe", icon: "👁️" },
  { id: "ANALYZE", label: "Analyze", icon: "🧠" },
  { id: "DNA", label: "Workflow DNA", icon: "🧬" },
  { id: "BLUEPRINT", label: "Blueprint", icon: "📐" },
  { id: "REPLAY", label: "Ghost Replay", icon: "👻" },
  { id: "DEPLOY", label: "Deploy Pipeline", icon: "⚙️" },
  { id: "OPERATIONS", label: "Live Operations", icon: "🚀" },
];


export const ProgressStoryBar: React.FC<ProgressStoryBarProps> = ({
  currentStage,
  unlockedStages,
  onSelectStage,
}) => {
  return (
    <div className="flex items-center justify-between gap-1 rounded-xl border border-slate-800/80 bg-slate-950/60 p-2 shadow-inner">
      {STAGES.map((s, idx) => {
        const isUnlocked = unlockedStages.includes(s.id);
        const isActive = currentStage === s.id;

        return (
          <React.Fragment key={s.id}>
            <button
              disabled={!isUnlocked}
              onClick={() => onSelectStage(s.id)}
              className={`flex flex-1 items-center justify-center gap-1.5 rounded-lg py-1.5 px-2 text-xs font-semibold transition-all duration-200 ${
                isActive
                  ? "bg-cyan-500 text-slate-950 font-bold shadow-md shadow-cyan-500/20"
                  : isUnlocked
                  ? "bg-slate-900 text-slate-200 hover:bg-slate-800"
                  : "bg-slate-950 text-slate-600 cursor-not-allowed opacity-50"
              }`}
            >
              <span className="text-xs">{s.icon}</span>
              <span className="hidden sm:inline text-[11px] truncate">{s.label}</span>
              {!isUnlocked && <Lock className="h-3 w-3 text-slate-600 shrink-0" />}
            </button>
            {idx < STAGES.length - 1 && <div className="h-4 w-[1px] bg-slate-800 shrink-0" />}
          </React.Fragment>
        );
      })}
    </div>
  );
};

"use client";

import React from "react";

export interface CandidateData {
  candidate_id: string;
  name: string;
  observed_steps: string[];

  occurrence_count: number;
  confidence_score: number; // 0.0 to 1.0
  success_rate: number; // 0.0 to 1.0
  applications_involved?: string[];
  discovered_at?: string;
}

export interface WorkflowCandidatesProps {
  candidates?: CandidateData[];
  onSelectCandidate?: (candidate: CandidateData) => void;
}

export const WorkflowCandidates: React.FC<WorkflowCandidatesProps> = ({
  candidates = [],
  onSelectCandidate,
}) => {
  if (candidates.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-700/60 bg-slate-900/40 p-8 text-center">
        <div className="rounded-full bg-slate-800/80 p-3 text-slate-400">
          <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <h4 className="mt-3 text-sm font-semibold text-slate-300">Continuous Observation Active</h4>
        <p className="mt-1 text-xs text-slate-500">Monitoring telemetry stream for recurring workflow patterns...</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400">
          Discovered Workflow Candidates ({candidates.length})
        </h3>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {candidates.map((cand) => {
          const confidencePct = Math.round(cand.confidence_score * 100);
          const successPct = Math.round(cand.success_rate * 100);

          return (
            <div
              key={cand.candidate_id}
              onClick={() => onSelectCandidate && onSelectCandidate(cand)}
              className="group relative flex flex-col justify-between rounded-xl border border-slate-800 bg-slate-900/80 p-5 shadow-lg backdrop-blur-sm transition-all duration-200 hover:border-cyan-500/50 hover:shadow-cyan-500/10 cursor-pointer"
            >
              {/* Card Header */}
              <div>
                <div className="flex items-start justify-between gap-2">
                  <h4 className="text-base font-bold text-slate-100 group-hover:text-cyan-400 transition-colors">
                    {cand.name}
                  </h4>
                  <span className="inline-flex items-center rounded-full bg-cyan-500/10 px-2.5 py-0.5 text-xs font-semibold text-cyan-400 border border-cyan-500/20">
                    {confidencePct}% Confidence
                  </span>
                </div>

                {/* Metrics Stats Row */}
                <div className="mt-3 flex items-center gap-4 text-xs text-slate-400">
                  <div className="flex items-center gap-1.5">
                    <span className="font-semibold text-slate-200">{cand.occurrence_count}</span>
                    <span>Occurrences</span>
                  </div>
                  <div className="h-3 w-[1px] bg-slate-800" />
                  <div className="flex items-center gap-1.5">
                    <span className="font-semibold text-emerald-400">{successPct}%</span>
                    <span>Success Rate</span>
                  </div>
                </div>

                {/* Steps Sequence Chips */}
                <div className="mt-4 flex flex-wrap gap-1.5">
                  {cand.observed_steps.map((step, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center gap-1 rounded bg-slate-800/80 px-2 py-1 text-[11px] font-mono text-slate-300 border border-slate-700/50"
                    >
                      <span className="text-[9px] font-bold text-cyan-400">{idx + 1}</span>
                      {step}
                    </span>
                  ))}
                </div>
              </div>

              {/* Card Footer */}
              <div className="mt-4 pt-3 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-500">
                <span>Apps: {cand.applications_involved?.join(", ") || "Web App"}</span>
                <span className="font-medium text-cyan-400 group-hover:underline">View Flow &rarr;</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

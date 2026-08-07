# GhostTrace Core System Rules

## Immutable Upstream Engine Contract (Commit f111128)

> [!CRITICAL]
> **STRICT IMMUTABILITY RULE**: The upstream telemetry, pattern recognition, mistake detection, and state machine pipeline up to the "Analyze Workflow" button lock/unlock state (commit `f111128`) is 100% verified and **STRICTLY IMMUTABLE**.

### Protected Components (DO NOT EDIT OR TOUCH UNDER ANY CIRCUMSTANCES):
1. **Telemetry & Window Ingestion**: `backend/app/api/routes/telemetry.py`, `backend/app/agents/telemetry/transfer_builder.py`, `backend/app/agents/telemetry/semantic_normalizer.py`.
2. **Pattern Discovery & Memory**: `backend/app/agents/pattern_discovery/mapping_memory.py`, `backend/app/agents/pattern_discovery/learning_planner.py`, `backend/app/agents/pattern_discovery/pattern_discovery_agent.py`.
3. **Mistake Detection & HITL Refinement**: `backend/app/agents/pattern_discovery/deviation_detector.py`, `backend/app/agents/pattern_discovery/correction_memory.py`.
4. **State Machine & Dashboard Polling**: `backend/app/api/routes/state.py` (polling & refine handlers), `frontend/src/components/candidate/WorkflowCandidatePanel.tsx`, `frontend/src/components/command-center/CommandCenterDashboard.tsx`.

### Allowed Scope for Future Tasks:
- Debugging, enhancements, and features must focus **EXCLUSIVELY** on downstream stages starting from **Workflow DNA onwards**:
  - `Workflow DNA` (rendering, graph visualization, modal)
  - `Automation Blueprint`
  - `Playwright Code Compiler`
  - `Ghost Replay Simulation`
  - `Self-Healing Engine`

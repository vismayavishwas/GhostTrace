export const STATE_MACHINE_NODES = [
  { id: "IDLE", label: "Idle Observer", phase: "Perception" },
  { id: "OBSERVING", label: "Telemetry Stream", phase: "Perception" },
  { id: "PATTERN_DISCOVERY", label: "Pattern Mining", phase: "Intelligence Core" },
  { id: "INTENT_VALIDATION", label: "Intent Disambiguation (HITL)", phase: "Intelligence Core" },
  { id: "WORKFLOW_DNA", label: "Workflow DNA Extractor", phase: "Intelligence Core" },
  { id: "CODE_GENERATION", label: "Code Compiler", phase: "Automation Factory" },
  { id: "SANDBOX", label: "Sandbox Runner", phase: "Automation Factory" },
  { id: "SELF_HEAL", label: "Self-Healing Engine", phase: "Automation Factory" },
  { id: "EXECUTION", label: "Production Runner", phase: "Execution & Governance" },
  { id: "CONTINUOUS_OBSERVATION", label: "Background Observer", phase: "Execution & Governance" },
] as const;

import { API_BASE_URL, WS_TELEMETRY_URL, WS_STATE_URL } from "./config";

export const DEFAULT_API_URL = API_BASE_URL;
export const DEFAULT_WS_TELEMETRY = WS_TELEMETRY_URL;
export const DEFAULT_WS_STATE = WS_STATE_URL;


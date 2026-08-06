from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Field, ConfigDict

from app.models.enums import LangGraphState, AgentStatus
from app.models.session import SessionState
from app.models.telemetry import TelemetryEvent
from app.models.workflow import WorkflowCandidate, WorkflowDNA, IntentDecision
from app.models.execution import SandboxResult, AutomationTask


class GhostTraceStateModel(BaseModel):
    """
    Central shared state object representing the full system context during state machine transitions.
    Used by LangGraph nodes and orchestrators.
    """
    current_state: LangGraphState = Field(default=LangGraphState.IDLE, description="Active state in state machine")
    session: SessionState = Field(default_factory=SessionState, description="Session tracking metadata")
    
    telemetry_buffer: List[TelemetryEvent] = Field(default_factory=list, description="Ingested telemetry event stream")
    candidates: List[WorkflowCandidate] = Field(default_factory=list, description="Discovered candidate workflow patterns")
    active_candidate: Optional[WorkflowCandidate] = Field(default=None, description="Candidate currently undergoing validation")
    
    intent_decisions: List[IntentDecision] = Field(default_factory=list, description="Human-in-the-loop decisions log")
    workflow_dna: Optional[WorkflowDNA] = Field(default=None, description="Extracted semantic Workflow DNA")
    
    generated_code: Optional[str] = Field(default=None, description="Synthesized Python/Playwright code")
    sandbox_results: List[SandboxResult] = Field(default_factory=list, description="History of sandbox execution attempts")
    active_task: Optional[AutomationTask] = Field(default=None, description="Active production automation task")
    
    self_heal_count: int = Field(default=0, ge=0, description="Number of self-healing iterations performed")
    agent_statuses: Dict[str, AgentStatus] = Field(default_factory=dict, description="Map of sub-agent statuses")
    error_log: List[str] = Field(default_factory=list, description="Accumulated system error messages")
    
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last state update timestamp")

    model_config = ConfigDict(use_enum_values=True)


class GhostTraceStateDict(TypedDict, total=False):
    """
    TypedDict representation of GhostTraceState for direct LangGraph compatibility.
    """
    current_state: str
    session: Dict[str, Any]
    telemetry_buffer: List[Dict[str, Any]]
    candidates: List[Dict[str, Any]]
    active_candidate: Optional[Dict[str, Any]]
    intent_decisions: List[Dict[str, Any]]
    workflow_dna: Optional[Dict[str, Any]]
    generated_code: Optional[str]
    sandbox_results: List[Dict[str, Any]]
    active_task: Optional[Dict[str, Any]]
    self_heal_count: int
    agent_statuses: Dict[str, str]
    error_log: List[str]
    updated_at: str


# Alias GhostTraceState to GhostTraceStateModel for standard use
GhostTraceState = GhostTraceStateModel

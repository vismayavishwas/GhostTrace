from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from uuid import uuid4
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import LangGraphState
from app.models.telemetry import TelemetryEvent
from app.models.workflow import WorkflowCandidate, WorkflowDNA, IntentDecision
from app.models.execution import SandboxResult
from app.agents.compiler.models import CodeArtifact
from app.agents.self_healing.models import HealingSummary
from app.agents.continuous_observer.models import ObservationEvent, ObserverNotification


class GhostTraceGraphState(BaseModel):
    """
    Shared State Schema for the GhostTrace AI LangGraph Orchestration State Machine.
    Tracks state transitions, telemetry, candidates, DNA, generated code, sandbox results,
    self-healing evolution lineage, and final execution status.
    """
    session_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique orchestrator session ID")
    workflow_id: Optional[str] = Field(default=None, description="Associated Workflow DNA ID")
    
    current_state: LangGraphState = Field(default=LangGraphState.IDLE, description="Current graph node state")
    
    telemetry_events: List[TelemetryEvent] = Field(default_factory=list, description="Ingested telemetry events")
    observations: List[ObservationEvent] = Field(default_factory=list, description="Continuous observation events")
    discovered_candidates: List[WorkflowCandidate] = Field(default_factory=list, description="Discovered workflow candidates")
    validated_intent: Optional[IntentDecision] = Field(default=None, description="Validated intent decision (APPROVED/BRANCH/MISTAKE)")
    workflow_dna: Optional[WorkflowDNA] = Field(default=None, description="Synthesized WorkflowDNA model")
    generated_code: Optional[CodeArtifact] = Field(default=None, description="Compiled Playwright CodeArtifact")
    sandbox_results: List[SandboxResult] = Field(default_factory=list, description="History of sandbox validation results")
    healing_summary: Optional[HealingSummary] = Field(default=None, description="Self-healing iteration summary")
    execution_status: Optional[SandboxResult] = Field(default=None, description="Production automation execution result")
    observation_feedback: List[ObserverNotification] = Field(default_factory=list, description="Continuous observer notifications")
    
    is_completed: bool = Field(default=False, description="Flag indicating clean graph termination")
    is_failed: bool = Field(default=False, description="Flag indicating graph failure termination")
    error_message: Optional[str] = Field(default=None, description="Terminal error details if failed")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="State creation timestamp")

    model_config = ConfigDict(use_enum_values=True)

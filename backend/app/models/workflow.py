from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from uuid import uuid4
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import IntentChoice
from app.models.telemetry import TelemetryEvent


class WorkflowCandidate(BaseModel):
    """
    Represents a repeated sequence of telemetry events identified as a candidate workflow.
    References event IDs to minimize memory and maintain full trace lineage.
    """
    candidate_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique candidate workflow ID")
    sequence_event_ids: List[str] = Field(default_factory=list, description="List of referenced TelemetryEvent IDs in order")
    sequence: List[TelemetryEvent] = Field(default_factory=list, description="Sequence of telemetry events in pattern")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Statistical pattern confidence score (0.0 - 1.0)")
    repetition_count: int = Field(default=1, ge=1, description="Number of times sequence was observed")
    description: str = Field(default="", description="Human-readable summary of pattern")
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of pattern detection")

    model_config = ConfigDict(use_enum_values=True)



class WorkflowDNAStep(BaseModel):
    """
    High-level semantic business operation step in Workflow DNA.
    """
    step_number: int = Field(..., ge=1, description="1-indexed sequence step number")
    action_name: str = Field(..., description="Abstract business operation name (e.g. 'Navigate to Portal', 'Input Invoice ID')")
    target_app: str = Field(..., description="Target application context (e.g. 'Zendesk', 'Excel', 'SAP')")
    selector: Optional[str] = Field(default=None, description="Primary UI element selector")
    fallback_selectors: List[str] = Field(default_factory=list, description="Backup selectors for self-healing resilience")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Semantic parameters (e.g. input placeholders)")

    model_config = ConfigDict(use_enum_values=True)


class WorkflowDNA(BaseModel):
    """
    Abstract semantic representation ('Workflow DNA') of a discovered process.
    """
    workflow_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique workflow DNA identifier")
    name: str = Field(..., description="Descriptive workflow title")
    description: str = Field(default="", description="Detailed summary of semantic workflow")
    steps: List[WorkflowDNAStep] = Field(default_factory=list, description="Ordered list of semantic business steps")
    inputs_schema: Dict[str, Any] = Field(default_factory=dict, description="Input parameters schema required to run workflow")
    output_schema: Dict[str, Any] = Field(default_factory=dict, description="Expected output data schema")
    applications_involved: List[str] = Field(default_factory=list, description="List of applications/websites involved in workflow")
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Overall confidence score of workflow candidate")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata and lineage references")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp when DNA was extracted")

    model_config = ConfigDict(use_enum_values=True)



class IntentDecision(BaseModel):
    """
    Human-in-the-loop decision record classifying a workflow variation or edge case.
    """
    decision_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique decision ID")
    candidate_id: str = Field(..., description="Associated workflow candidate ID")
    choice: IntentChoice = Field(..., description="Human decision (MISTAKE, BRANCH, APPROVED, REJECTED)")
    reason: Optional[str] = Field(default=None, description="Ambiguity detection reason for HITL UI display")
    feedback_comment: Optional[str] = Field(default=None, description="Optional user explanation or feedback")
    decided_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of human decision")

    model_config = ConfigDict(use_enum_values=True)


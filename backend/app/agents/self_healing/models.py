from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from uuid import uuid4
from pydantic import BaseModel, Field, ConfigDict
from app.models.execution import SandboxResult


class FailureDiagnosis(BaseModel):
    """
    Structured diagnosis extracted from a failed SandboxResult and CodeArtifact.
    Isolates debugging & traceback analysis from the LLM repair engine.
    """
    diagnosis_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique diagnosis ID")
    artifact_id: str = Field(..., description="Target CodeArtifact identifier")
    workflow_id: str = Field(..., description="Target Workflow DNA identifier")
    
    failing_line: Optional[int] = Field(default=None, description="Parsed 1-indexed failing line number in source code")
    failing_step_number: Optional[int] = Field(default=None, description="Matched WorkflowDNA step number from step_map")
    failing_step_name: Optional[str] = Field(default=None, description="Matched step action name")
    failing_selector: Optional[str] = Field(default=None, description="UI selector that caused runtime error")
    
    probable_cause: str = Field(default="Unknown Runtime Error", description="Categorized cause (Syntax, Selector, Timeout)")
    healing_level: str = Field(default="Level 1 — Selector Healing", description="Self-healing level (Level 1 Selector, Level 2 Locator, Level 3 Structural, Level 4 Semantic, Level 5 Intent)")
    traceback: str = Field(default="", description="Full captured Python exception traceback")

    surrounding_code: str = Field(default="", description="Code snippet surrounding the failing line")
    repair_prompt: str = Field(default="", description="Structured prompt constructed for Gemini repair engine")

    model_config = ConfigDict(use_enum_values=True)


class HealingRecord(BaseModel):
    """
    Complete audit record for a single self-healing attempt.
    Preserves tracebacks, prompts, model outputs, and version transitions.
    """
    record_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique healing record ID")
    attempt_number: int = Field(..., ge=1, description="1-indexed repair attempt number")
    workflow_id: str = Field(..., description="Target Workflow DNA identifier")
    
    failing_artifact_id: str = Field(..., description="Input failing CodeArtifact ID")
    repaired_artifact_id: str = Field(..., description="Output repaired CodeArtifact ID")
    failing_version: int = Field(default=1, ge=1, description="Source artifact version number")
    repaired_version: int = Field(default=2, ge=1, description="Repaired artifact version number")
    
    failing_line: Optional[int] = Field(default=None, description="Failing line number")
    failing_step_name: Optional[str] = Field(default=None, description="Name of failing step")
    healing_level: str = Field(default="Level 1 — Selector Healing", description="Self-healing level executed")

    
    original_traceback: str = Field(default="", description="Original error traceback before repair")
    patched_traceback: Optional[str] = Field(default=None, description="New traceback if repair attempt failed, or None if passed")
    
    repair_prompt: str = Field(default="", description="Structured prompt sent to repair engine")
    model_output: str = Field(default="", description="Raw code / explanation output from repair engine")
    
    status: str = Field(default="PASS", description="Execution status of repaired artifact ('PASS' or 'FAIL')")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of repair record")

    model_config = ConfigDict(use_enum_values=True)


class HealingSummary(BaseModel):
    """
    Overall self-healing execution summary containing version evolution lineage.
    """
    workflow_id: str = Field(..., description="Target Workflow DNA identifier")
    overall_status: str = Field(..., description="'PASS' if resolved within budget, 'FAIL' if retries exhausted")
    total_attempts: int = Field(..., ge=0, description="Total repair attempts executed")
    final_version: int = Field(..., ge=1, description="Final code version number")
    
    repair_history: List[HealingRecord] = Field(default_factory=list, description="Ordered history of repair records (v1 -> v2 -> v3)")
    final_sandbox_result: SandboxResult = Field(..., description="Final SandboxResult after healing")

    model_config = ConfigDict(use_enum_values=True)

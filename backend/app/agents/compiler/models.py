from datetime import datetime, timezone
from typing import Dict, Any, Optional
from uuid import uuid4
from pydantic import BaseModel, Field, ConfigDict


class CodeArtifact(BaseModel):
    """
    Synthesized production-grade Playwright Python source code artifact.
    Includes step mapping for precise self-healing traceback diagnosis.
    """
    artifact_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique code artifact ID")
    workflow_id: str = Field(..., description="Associated Workflow DNA identifier")
    
    source_code: str = Field(..., description="Executable Python Playwright source code")
    language: str = Field(default="python", description="Target programming language")
    framework: str = Field(default="playwright", description="Target automation framework")
    
    # Step mapping for Self-Healing line diagnosis: step_number -> metadata (action_name, function_name, line_start, line_end)
    step_map: Dict[int, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Mapping between WorkflowDNA step numbers and generated modular code sections/lines"
    )
    
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Generation metadata and parameters")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of code generation")

    model_config = ConfigDict(use_enum_values=True)

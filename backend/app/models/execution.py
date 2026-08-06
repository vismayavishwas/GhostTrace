from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from uuid import uuid4
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import AgentStatus


class SandboxResult(BaseModel):
    """
    Execution result captured from running generated automation code in isolated Sandbox.
    """
    execution_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique sandbox execution ID")
    success: bool = Field(..., description="Whether the sandbox run completed without unhandled errors")
    duration_ms: float = Field(default=0.0, ge=0.0, description="Execution duration in milliseconds")
    
    stdout: str = Field(default="", description="Captured standard output")
    stderr: str = Field(default="", description="Captured error output")
    
    error_traceback: Optional[str] = Field(default=None, description="Python exception traceback if execution failed")
    failing_selector: Optional[str] = Field(default=None, description="UI selector that caused runtime failure")
    failing_line: Optional[int] = Field(default=None, description="Line number of failure in generated code")
    
    artifacts: List[str] = Field(default_factory=list, description="Paths to captured artifacts (screenshots, traces)")
    executed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of sandbox run")

    model_config = ConfigDict(use_enum_values=True)


class AutomationTask(BaseModel):
    """
    Task definition for production workflow execution.
    """
    task_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique production task ID")
    workflow_id: str = Field(..., description="Associated Workflow DNA identifier")
    target_app: str = Field(default="Web Application", description="Target application name")
    
    status: AgentStatus = Field(default=AgentStatus.IDLE, description="Current execution status")
    retry_count: int = Field(default=0, ge=0, description="Current retry attempt count")
    max_retries: int = Field(default=3, ge=1, description="Maximum allowed retries before flagging failure")
    
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters passed to automation runner")
    error_history: List[str] = Field(default_factory=list, description="Historical log of execution error messages")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Task creation timestamp")

    model_config = ConfigDict(use_enum_values=True)

from datetime import datetime, timezone
from typing import Optional, Callable, List, Union, Awaitable
from uuid import uuid4
from pydantic import BaseModel, Field, ConfigDict


class ExecutionProgress(BaseModel):
    """
    Real-time progress update event emitted during workflow automation execution.
    """
    progress_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique progress event ID")
    execution_id: str = Field(..., description="Target execution run ID")
    workflow_id: str = Field(..., description="Target Workflow DNA ID")
    
    step_number: int = Field(..., ge=0, description="Current step index (0 for startup/cleanup)")
    total_steps: int = Field(..., ge=1, description="Total workflow steps count")
    action_name: str = Field(..., description="Human-readable action name (e.g. 'Navigate to SAP ERP')")
    
    status: str = Field(
        default="RUNNING",
        description="Execution status ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED')"
    )
    elapsed_ms: float = Field(default=0.0, ge=0.0, description="Milliseconds elapsed since execution start")
    error_message: Optional[str] = Field(default=None, description="Error message if step failed")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Progress timestamp")

    model_config = ConfigDict(use_enum_values=True)


class ProgressTracker:
    """
    Helper for building and tracking ExecutionProgress state transitions.
    """
    def __init__(self, execution_id: str, workflow_id: str, total_steps: int):
        self.execution_id = execution_id
        self.workflow_id = workflow_id
        self.total_steps = total_steps

    def create_progress(
        self,
        step_number: int,
        action_name: str,
        status: str = "RUNNING",
        elapsed_ms: float = 0.0,
        error_message: Optional[str] = None
    ) -> ExecutionProgress:
        """Factory creating a validated ExecutionProgress instance."""
        return ExecutionProgress(
            execution_id=self.execution_id,
            workflow_id=self.workflow_id,
            step_number=step_number,
            total_steps=self.total_steps,
            action_name=action_name,
            status=status,
            elapsed_ms=elapsed_ms,
            error_message=error_message
        )

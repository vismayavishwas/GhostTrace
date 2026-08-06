from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, Field, ConfigDict


class SessionState(BaseModel):
    """
    Session-level metadata and tracking metrics for active observation sessions.
    """
    session_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique session ID")
    active_workflow_id: Optional[str] = Field(default=None, description="Currently executing or discovered workflow ID")
    total_events_captured: int = Field(default=0, ge=0, description="Total telemetry events captured in session")
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Session start timestamp")
    last_active_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last recorded user activity timestamp")

    model_config = ConfigDict(use_enum_values=True)

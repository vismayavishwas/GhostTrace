from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from uuid import uuid4
from pydantic import BaseModel, Field, ConfigDict


class ReplayFrame(BaseModel):
    """
    Timestamped frame object representing a single captured cursor/interaction state.
    Includes viewport and scroll offset context for responsive screen scaling.
    """
    frame_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique frame identifier")
    frame_index: int = Field(..., ge=0, description="0-indexed sequence position")
    timestamp_ms: float = Field(..., ge=0.0, description="Relative timestamp in milliseconds")
    
    x: float = Field(..., description="Mouse x coordinate in pixels")
    y: float = Field(..., description="Mouse y coordinate in pixels")
    
    viewport_width: int = Field(default=1920, ge=1, description="Browser viewport width at capture")
    viewport_height: int = Field(default=1080, ge=1, description="Browser viewport height at capture")
    scroll_x: float = Field(default=0.0, description="Horizontal scroll offset at capture")
    scroll_y: float = Field(default=0.0, description="Vertical scroll offset at capture")
    
    event_type: str = Field(default="mousemove", description="Event type ('mousemove', 'click', 'keydown', 'input', 'scroll')")
    target_selector: Optional[str] = Field(default=None, description="CSS selector of target element")
    element_tag: Optional[str] = Field(default=None, description="HTML tag name")
    is_click: bool = Field(default=False, description="Flag indicating click event triggering ripple animation")
    text_value: Optional[str] = Field(default=None, description="Input text value if applicable")

    model_config = ConfigDict(use_enum_values=True)


class ReplaySessionState(BaseModel):
    """
    State of an active ghost replay playback session.
    """
    session_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique replay session ID")
    workflow_id: str = Field(..., description="Target Workflow Candidate ID")
    status: str = Field(default="IDLE", description="Status ('IDLE', 'PLAYING', 'PAUSED', 'STOPPED')")
    speed_multiplier: float = Field(default=1.0, description="Playback speed (0.25x, 0.5x, 1x, 1.5x, 2x, 4x)")
    current_time_ms: float = Field(default=0.0, description="Current playback position in milliseconds")
    total_duration_ms: float = Field(default=0.0, description="Total sequence duration in milliseconds")
    total_frames: int = Field(default=0, ge=0, description="Total frames count")
    current_frame_index: int = Field(default=0, ge=0, description="Current active frame index")

    model_config = ConfigDict(use_enum_values=True)

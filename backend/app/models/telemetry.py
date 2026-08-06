from datetime import datetime, timezone
from typing import Optional, Dict, Any
from uuid import uuid4
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import EventType


class TelemetryEvent(BaseModel):
    """
    Represents a single perception telemetry event captured from user interaction.
    """
    event_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique telemetry event ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="UTC timestamp of the event")
    event_type: EventType = Field(..., description="Category of user interaction event")
    
    coordinates_x: Optional[int] = Field(default=None, description="Cursor X coordinate on target screen/viewport")
    coordinates_y: Optional[int] = Field(default=None, description="Cursor Y coordinate on target screen/viewport")
    
    target_selector: Optional[str] = Field(default=None, description="CSS or XPath element selector")
    element_tag: Optional[str] = Field(default=None, description="HTML DOM tag name (e.g. BUTTON, INPUT)")
    input_value: Optional[str] = Field(default=None, description="Typed text value or key value")
    
    dom_snapshot: Optional[str] = Field(default=None, description="HTML DOM snippet or outerHTML string")
    app_title: str = Field(default="Unknown Application", description="Title of active window or web application")
    
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Flexible dictionary for extra perception metadata")

    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={datetime: lambda dt: dt.isoformat()}
    )

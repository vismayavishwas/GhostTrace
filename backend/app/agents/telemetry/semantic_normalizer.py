from typing import Optional, List, Dict, Any
from app.models.telemetry import TelemetryEvent, TelemetryEventType

class SemanticEvent:
    """
    Normalized business event extracted from raw browser telemetry.
    Preserves raw event reference for precise high-fidelity replay.
    """
    def __init__(self, raw_event: TelemetryEvent, semantic_type: str, business_label: str):
        self.raw_event = raw_event
        self.event_id = raw_event.event_id
        self.semantic_type = semantic_type
        self.business_label = business_label
        self.target_selector = raw_event.target_selector
        self.element_tag = raw_event.element_tag
        self.app_title = raw_event.app_title
        self.timestamp = raw_event.timestamp
        self.input_masked = raw_event.input_masked

    @property
    def event_type(self):
        return self.semantic_type

    def to_dict((self)) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "semantic_type": self.semantic_type,
            "business_label": self.business_label,
            "target_selector": self.target_selector,
            "app_title": self.app_title,
            "timestamp": self.timestamp.isoformat() if hasattr(self.timestamp, "isoformat") else str(self.timestamp),
            "raw_event_type": getattr(self.raw_event.event_type, "value", str(self.raw_event.event_type)),
        }


class SemanticNormalizer:
    """
    Architectural pipeline stage: Transforms raw telemetry events into semantic business operations.
    Evaluates: 'Does this event contribute business meaning?'
    """
    
    BUSINESS_EVENT_TYPES = {
        "COPY", "PASTE", "TYPE", "SUBMIT", "SELECT_OPTION",
        "UPLOAD_FILE", "CHECKBOX", "OPEN_DROPDOWN", "EXECUTE_ACTION"
    }

    BUSINESS_TAGS = {"INPUT", "TEXTAREA", "SELECT", "OPTION", "FORM"}

    @classmethod
    def normalize(cls, raw_event: TelemetryEvent) -> Optional[SemanticEvent]:
        """
        Normalizes raw telemetry event to SemanticEvent if it possesses business meaning.
        Returns None for non-semantic layout noise (e.g., clicking background divs, h1 tags, svg icons).
        """
        raw_type_str = str(raw_event.event_type.value if hasattr(raw_event.event_type, "value") else raw_event.event_type).upper()
        selector = str(raw_event.target_selector or "").lower()
        tag = str(raw_event.element_tag or "").upper()

        # 1. Direct Business Operations (COPY, PASTE, TYPE, SUBMIT, etc.)
        for bus_type in cls.BUSINESS_EVENT_TYPES:
            if bus_type in raw_type_str:
                label = f"{bus_type} on {raw_event.target_selector or 'Field'}"
                return SemanticEvent(raw_event, bus_type, label)

        # 2. Form Field Interactions (CLICK on input/textarea/select -> FOCUS_FIELD)
        if raw_type_str == "CLICK" and (tag in cls.BUSINESS_TAGS or any(k in selector for k in ["source", "target", "input", "field", "form"])):
            label = f"FOCUS_FIELD on {raw_event.target_selector or 'Field'}"
            return SemanticEvent(raw_event, "FOCUS_FIELD", label)

        # 3. Action Buttons with explicit submit/action intent
        if raw_type_str == "CLICK" and ("button" in selector and any(k in selector for k in ["submit", "save", "confirm", "process", "next"])):
            label = f"SUBMIT_ACTION on {raw_event.target_selector}"
            return SemanticEvent(raw_event, "SUBMIT_ACTION", label)

        # Non-semantic layout noise (generic wrapper clicks on span, div, svg, h1) -> Filtered out for pattern discovery
        return None

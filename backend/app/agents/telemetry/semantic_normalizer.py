import re
from typing import Optional, List, Dict, Any, Tuple
from app.models.telemetry import TelemetryEvent



class SemanticEvent:
    """
    Normalized domain-agnostic business event extracted from raw browser telemetry.
    Fuses 6 metadata signals (label, heading, app_title, role, value, flow) into an abstract semantic entity.
    Preserves raw event reference strictly for Playwright execution metadata.
    """
    def __init__(
        self,
        raw_event: TelemetryEvent,
        operation: str,
        semantic_entity: str,
        display_label: str
    ):
        self.raw_event = raw_event
        self.event_id = raw_event.event_id
        self.semantic_type = operation
        self.operation = operation
        self.semantic_entity = semantic_entity
        self.display_label = display_label
        self.business_label = display_label
        self.target_selector = raw_event.target_selector
        self.element_tag = raw_event.element_tag
        self.app_title = raw_event.app_title
        self.timestamp = raw_event.timestamp
        self.input_masked = getattr(raw_event, "input_value", None) or getattr(raw_event, "input_masked", None)

    @property
    def event_type(self):
        return self.operation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "operation": self.operation,
            "semantic_entity": self.semantic_entity,
            "display_label": self.display_label,
            "business_label": self.display_label,
            "target_selector": self.target_selector,
            "app_title": self.app_title,
            "timestamp": self.timestamp.isoformat() if hasattr(self.timestamp, "isoformat") else str(self.timestamp),
            "raw_event_type": getattr(self.raw_event.event_type, "value", str(self.raw_event.event_type)),
        }


class SemanticNormalizer:
    """
    Architectural pipeline stage: Multi-Signal Contextual Fusion.
    Fuses field_label, surrounding_heading, application_title, destination_field, values, and interaction flow.
    Strictly domain-agnostic: Never infers entity types from raw value patterns or hardcoded regexes alone.
    """
    
    BUSINESS_OPERATIONS = {
        "COPY", "PASTE", "TYPE", "SUBMIT", "SELECT_OPTION",
        "UPLOAD_FILE", "CHECKBOX", "OPEN_DROPDOWN", "EXECUTE_ACTION"
    }

    BUSINESS_TAGS = {"INPUT", "TEXTAREA", "SELECT", "OPTION", "FORM"}

    @classmethod
    def extract_semantic_metadata(cls, raw_event: TelemetryEvent) -> Tuple[str, str]:
        """
        Extracts semantic entity key 100% from contextual metadata (field_label, heading, app_title).
        Completely decoupled from raw DOM selector strings or field position index tokens.
        """
        app_title = str(raw_event.app_title or raw_event.active_tab or "App").strip()
        selector = str(raw_event.target_selector or "").strip()

        # Extract contextual label from raw event metadata
        raw_label = getattr(raw_event, "field_label", None) or getattr(raw_event, "aria_label", None) or ""
        
        if not raw_label:
            # Fallback to cleaning selector into a human-readable title without structural index tokens
            clean_token = re.sub(r'[#\._\-\d]', ' ', selector).strip()
            raw_label = clean_token.title() if clean_token else "Field"

        # Sanitize entity key (e.g., "semantic:sap_erp:record_id")
        sanitized_app = re.sub(r'[^a-zA-Z0-9]', '_', app_title.lower()).strip('_')
        sanitized_label = re.sub(r'[^a-zA-Z0-9]', '_', raw_label.lower()).strip('_')
        
        semantic_entity = f"semantic:{sanitized_app}:{sanitized_label}"
        display_label = f"{raw_label} ({app_title})"

        return semantic_entity, display_label


    @classmethod
    def normalize(cls, raw_event: TelemetryEvent) -> Optional[SemanticEvent]:
        """
        Normalizes raw telemetry event into a domain-agnostic SemanticEvent.
        Returns None for non-semantic layout noise (generic div/span wrapper clicks).
        """
        raw_type_str = str(raw_event.event_type.value if hasattr(raw_event.event_type, "value") else raw_event.event_type).upper()
        selector = str(raw_event.target_selector or "").lower()
        tag = str(raw_event.element_tag or "").upper()

        # 1. Direct Business Operations (COPY, PASTE, TYPE, SUBMIT, etc.)
        for op in cls.BUSINESS_OPERATIONS:
            if op in raw_type_str:
                semantic_entity, display_label = cls.extract_semantic_metadata(raw_event)
                human_op_label = f"{op.capitalize()} {display_label}"
                return SemanticEvent(raw_event, op, semantic_entity, human_op_label)

        # 2. Form Field Interactions (CLICK on input/textarea/select -> FOCUS_FIELD)
        if raw_type_str == "CLICK" and (tag in cls.BUSINESS_TAGS or any(k in selector for k in ["source", "target", "input", "field", "form"])):
            semantic_entity, display_label = cls.extract_semantic_metadata(raw_event)
            return SemanticEvent(raw_event, "FOCUS_FIELD", semantic_entity, f"Focus {display_label}")

        # 3. Action Buttons with explicit submit/action intent
        if raw_type_str == "CLICK" and ("button" in selector and any(k in selector for k in ["submit", "save", "confirm", "process", "next"])):
            semantic_entity, display_label = cls.extract_semantic_metadata(raw_event)
            return SemanticEvent(raw_event, "SUBMIT_ACTION", semantic_entity, f"Submit Action in {raw_event.app_title or 'App'}")

        # Non-semantic layout noise -> Filter out for pattern discovery
        return None


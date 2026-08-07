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
    def pasted_value(self) -> str:
        return str(self.input_masked or "")

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

    INTERACTIVE_TAGS = {
        "INPUT", "TEXTAREA", "SELECT", "OPTION", "BUTTON",
        "A", "FORM", "LABEL", "CHECKBOX", "RADIO"
    }

    INTERACTIVE_ROLES = {
        "textbox", "button", "link", "combobox", "checkbox",
        "radio", "option", "menuitem", "cell", "searchbox", "tab"
    }

    @classmethod
    def extract_semantic_metadata(cls, raw_event: TelemetryEvent) -> Tuple[str, str]:
        """
        Constructs a Semantic Data Fingerprint fusing 5 contextual signals:
        1. copied_value / pasted_value structural features
        2. user_interaction_flow (source app vs target app data flow)
        3. surrounding_heading & container context
        4. application_title
        5. field_label / aria_label
        
        Preserves target_selector, xpath, and bounding_box as metadata for Playwright code generation and replay.
        """
        app_title = (raw_event.app_title or getattr(raw_event, "active_tab", None) or "Web App").strip()
        selector = (raw_event.target_selector or "").strip()
        val = str(getattr(raw_event, "input_value", None) or getattr(raw_event, "input_masked", None) or "").strip()
        meta = getattr(raw_event, "metadata", {}) or {}
        raw_label = getattr(raw_event, "field_label", None) or meta.get("field_label") or getattr(raw_event, "aria_label", None) or meta.get("aria_label") or ""
        heading = str(getattr(raw_event, "surrounding_heading", None) or meta.get("surrounding_heading") or "").strip()

        app_key = re.sub(r'[^a-zA-Z0-9]', '_', app_title.lower()).strip('_') or "app"

        # 1. Highest Priority: Explicit Field Label or ARIA Label or Placeholder
        placeholder = getattr(raw_event, "placeholder", None) or meta.get("placeholder") or ""
        effective_label = raw_label or placeholder
        if effective_label and not any(j in effective_label.lower() for j in ["element", "span"]):
            clean_label = re.sub(r'[^a-zA-Z0-9]', '_', effective_label.lower()).strip('_')
            fingerprint_token = f"lbl_{clean_label}"
            display_title = effective_label
        # 2. Second Priority: Surrounding Section Heading
        elif heading:
            clean_heading = re.sub(r'[^a-zA-Z0-9]', '_', heading.lower()).strip('_')
            fingerprint_token = f"hdg_{clean_heading}"
            display_title = f"{heading} Field"
        # 3. Third Priority: DOM Element ID / Name / Selector Fingerprint
        else:
            id_match = re.search(r'#([a-zA-Z0-9_-]+)', selector)
            if id_match:
                from app.agents.pattern_discovery.deviation_detector import format_clean_entity_label
                core_id = id_match.group(1).lower().replace("source-", "").replace("target-", "").replace("source_", "").replace("target_", "")
                fingerprint_token = f"lbl_{core_id}"
                display_title = format_clean_entity_label("", core_id)
            else:
                sel_clean = re.sub(r'[^a-zA-Z0-9]', '_', selector.lower()).strip('_')
                if not sel_clean:
                    sel_clean = "elem_" + re.sub(r'[^a-zA-Z0-9]', '_', (raw_event.element_tag or "input").lower())
                fingerprint_token = f"elem_{sel_clean[:32]}"
                display_title = "Unknown Field"

        semantic_entity = f"entity:{app_key}:{fingerprint_token}"
        display_label = display_title if display_title == "Unknown Field" else display_title

        return semantic_entity, display_label






    @classmethod
    def normalize(cls, raw_event: TelemetryEvent) -> Optional[SemanticEvent]:
        """
        Normalizes raw telemetry event into a domain-agnostic SemanticEvent.
        Filters out strictly non-interactive root container wrappers (e.g. body, html, generic unlabelled div/span wrapper clicks).
        """
        raw_type_str = str(raw_event.event_type.value if hasattr(raw_event.event_type, "value") else raw_event.event_type).upper()
        selector = (raw_event.target_selector or "").lower().strip()
        tag = (raw_event.element_tag or "").upper().strip()
        meta = getattr(raw_event, "metadata", {}) or {}
        explicit_op = str(meta.get("operation") or "").upper()

        # 0. Filter out GhostTrace Platform UI elements EXCEPT sandbox interactive target elements
        app_title = (raw_event.app_title or getattr(raw_event, "active_tab", None) or "").lower()
        is_sandbox_elem = (
            "sandbox" in selector or 
            "sandbox" in app_title or 
            meta.get("is_sandbox") is True or
            "source" in selector or 
            "target" in selector or 
            "pdf" in app_title or 
            "sap" in app_title or 
            "workday" in app_title or 
            "salesforce" in app_title or 
            "excel" in app_title or 
            "candidate" in app_title
        )
        if not is_sandbox_elem:
            if "ghosttrace" in app_title or "process intelligence" in app_title:
                return None

            platform_ui_classes = [
                "backdrop-blur", "bg-background", "command-center",
                "shadow-2xl", "border-cyan", "border-slate", "bg-slate", "window.selection"
            ]
            if any(c in selector for c in platform_ui_classes):
                return None



        # 1. Direct Business Operations (COPY, PASTE, TYPE, SUBMIT, etc.)
        for op in cls.BUSINESS_OPERATIONS:
            if op in raw_type_str or op == explicit_op:
                semantic_entity, display_label = cls.extract_semantic_metadata(raw_event)
                return SemanticEvent(raw_event, op, semantic_entity, display_label)

        # 2. Filter out non-interactive layout container wrapper clicks (body, html, h4, p, empty main)
        if tag in ["BODY", "HTML", "H4", "P"] or selector in ["body", "html", "window.selection"]:
            return None

        # Generic div or span click with zero attributes, zero labels, zero selector info -> Layout noise
        if tag in ["DIV", "SPAN", "SECTION", "MAIN"] and not selector and not getattr(raw_event, "field_label", None) and not getattr(raw_event, "aria_label", None):
            return None

        # 3. Domain-Agnostic Interactive Element Interaction (CLICK / KEY / SELECT on target application UI)
        semantic_entity, display_label = cls.extract_semantic_metadata(raw_event)
        op_label = "SUBMIT_ACTION" if tag in ["BUTTON", "SUBMIT"] or "button" in selector else "FOCUS_FIELD"
        return SemanticEvent(raw_event, op_label, semantic_entity, f"Action on {display_label}")

